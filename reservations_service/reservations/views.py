# reservations_service/reservations/views.py

from datetime import datetime

import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import Reservation
from .serializers import ReservationSerializer
from config.consul_registry import discover_service
import pika
import json
import os

# --- Frontend Imports ---
from django.shortcuts import render, redirect
# -------------------------

def publish_event(event_type, data):
    RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue='notifications')
        
        message = {
            "event": event_type,
            "data": data
        }
        channel.basic_publish(exchange='', routing_key='notifications', body=json.dumps(message))
        connection.close()
    except Exception as e:
        print(f"Failed to publish event: {e}")



def parse_iso_datetime(value: str):
    """
    Petite fonction utilitaire pour transformer une chaîne ISO8601
    (ex : '2025-12-09T17:53:38Z') en objet datetime.
    """
    if not value:
        return None
    try:
        # On remplace le 'Z' par '+00:00' pour que fromisoformat comprenne
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)
    except Exception:
        return None


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    # ... existing methods omitted for brevity if not changing logic ...
    # Wait, I must include the full class content or else it gets overwritten?
    # write_to_file overwrites. I cannot use replacement_chunks easily on large file re-write.
    # I will paste the existing class content.
    
    # 1) Récupérer l'utilisateur courant via auth_service
    def _get_current_user(self):
        auth_header = self.request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            # Try cookie if header missing (Wait, ViewSet context usually doesn't stick cookies to headers automatically)
            pass
            # raise ValidationError("Token manquant.")
        if not auth_header:
             raise ValidationError("Token manquant.")

        url = f"{settings.AUTH_SERVICE_URL}/users/me/"
        
        try:
            resp = requests.get(url, headers={"Authorization": auth_header}, timeout=5)
        except requests.RequestException as e:
            print(f"ERROR calling auth service: {e}", flush=True)
            raise ValidationError("Erreur du service d'authentification.")

        if resp.status_code != 200:
            print(f"Auth service returned {resp.status_code}: {resp.text}", flush=True)
            raise ValidationError("Erreur du service d'authentification.")

        return resp.json()

    # 2) Récupérer les infos de la séance via courses_service
    def _get_session_details(self, session_id: int):
        auth_header = self.request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
             raise ValidationError("Token manquant.")

        url = f"{settings.COURSES_SERVICE_URL}/sessions/{session_id}/"

        try:
            resp = requests.get(url, headers={"Authorization": auth_header}, timeout=5)
        except requests.RequestException as e:
            print(f"ERROR calling courses service: {e}", flush=True)
            raise ValidationError("Erreur du service des cours.")

        if resp.status_code == 404:
            raise ValidationError("Séance introuvable.")
        if resp.status_code != 200:
            print(f"Courses service returned {resp.status_code}: {resp.text}", flush=True)
            raise ValidationError(f"Erreur du service des cours (code {resp.status_code}).")

        return resp.json()

    # GET /api/reservations/my/  -> réservations de l'utilisateur connecté
    @action(detail=False, methods=["get"], url_path="my")
    def my_reservations(self, request):
        user_data = self._get_current_user()
        qs = self.get_queryset().filter(user_id=user_data["id"])
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Support filtering by session_id via query parameter
        session_id = request.query_params.get('session_id')
        if session_id is not None:
            try:
                queryset = queryset.filter(session_id=int(session_id))
            except ValueError:
                pass

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def perform_create(self, serializer):
        session_id = serializer.validated_data["session_id"]
        
        # Appel aux autres microservices
        session_data = self._get_session_details(session_id)
        user_data = self._get_current_user()

        # Règle 0 : refus si la séance est déjà terminée
        end_str = session_data.get("end_datetime")
        end_dt = parse_iso_datetime(end_str)
        if end_dt is not None and end_dt < timezone.now():
            raise ValidationError("Cette séance est déjà terminée.")

        # Règle 0 bis : refus si la séance a déjà commencé
        start_str = session_data.get("start_datetime")
        start_dt = parse_iso_datetime(start_str)
        if start_dt is not None and start_dt < timezone.now():
             raise ValidationError("Impossible de réserver une séance passée ou déjà commencée.")

        # Règle 1 : cet utilisateur a-t-il déjà réservé cette séance ?
        already_reserved = Reservation.objects.filter(
            user_id=user_data["id"],
            session_id=session_id,
            status="CONFIRMED",
        ).exists()
        if already_reserved:
            raise ValidationError("Vous avez déjà réservé cette séance.")

        # Règle 2 : contrôle de capacité
        capacity = session_data.get("capacity")
        if capacity is not None:
            confirmed_count = Reservation.objects.filter(
                session_id=session_id,
                status="CONFIRMED",
            ).count()
            if confirmed_count >= capacity:
                raise ValidationError("La séance est complète.")

        # Tout est bon -> création
        instance = serializer.save(
            user_id=user_data["id"],
            status="CONFIRMED",
        )
        
        # Publish notification
        try:
            publish_event("RESERVATION_CREATED", {
                "user_id": user_data["id"],
                "session_id": session_id,
                "reservation_id": instance.id
            })
        except Exception as e:
            print(f"Warning: Failed to publish event: {e}", flush=True)

    def destroy(self, request, *args, **kwargs):
        reservation = self.get_object()
        user_data = self._get_current_user()
        
        if reservation.user_id != user_data["id"]:
            user_role = user_data.get("role")
            if user_role != "ADMIN":
                raise ValidationError(
                    "Vous ne pouvez annuler que vos propres réservations."
                )

        if reservation.status == "CANCELLED":
            raise ValidationError("Cette réservation est déjà annulée.")

        reservation.status = "CANCELLED"
        reservation.save()

        serializer = self.get_serializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- Frontend Views ---

def my_reservations_view(request):
    user_id = getattr(getattr(request, 'user', None), 'id', None)
    if not user_id:
        return redirect('/auth/login')
        
    reservations = Reservation.objects.filter(user_id=user_id).exclude(status='CANCELLED').order_by('-created_at')
    
    res_data = []
    # Fetch details from Courses Service
    token = request.COOKIES.get('access_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    for res in reservations:
        title = f"Session #{res.session_id}"
        start_str = "TBD"
        
        try:
            # Correct URL based on router include
            url = f"http://courses-service:8002/api/sessions/{res.session_id}/"
            resp = requests.get(url, headers=headers, timeout=0.5)
            if resp.status_code == 200:
                d = resp.json()
                title = d.get('course', {}).get('title', title)
                start_str = d.get('start_datetime', start_str)
        except Exception:
            pass
            
        res_data.append({
            'object': res,
            'title': title,
            'start': start_str
        })
            
    return render(request, 'reservations/list.html', {'reservations': res_data})

def book_view(request, session_id):
    user_id = getattr(getattr(request, 'user', None), 'id', None)
    if not user_id: return redirect('/auth/login')
    
    if request.method == 'POST':
        # Create Reservation
        # We duplicate the creation logic slightly or just create.
        # For frontend demo simplicity:
        if not Reservation.objects.filter(user_id=user_id, session_id=session_id, status='CONFIRMED').exists():
            instance = Reservation.objects.create(user_id=user_id, session_id=session_id, status='CONFIRMED')
            # Trigger notification
            publish_event("RESERVATION_CREATED", {
                "user_id": user_id,
                "session_id": session_id,
                "reservation_id": instance.id
            })
            
        return redirect('/reservations/?success=1')
    
    # Confirm Page
    # Fetch session title for display
    token = request.COOKIES.get('access_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    title = f"Session #{session_id}"
    try:
        url = f"http://courses-service:8002/api/sessions/{session_id}/"
        resp = requests.get(url, headers=headers, timeout=1)
        if resp.status_code == 200:
            title = resp.json().get('course', {}).get('title', title)
    except:
        pass

    return render(request, 'reservations/book.html', {'session_id': session_id, 'title': title})

def cancel_frontend_view(request, pk):
    user_id = getattr(getattr(request, 'user', None), 'id', None)
    if not user_id: return redirect('/auth/login')
    
    try:
        res = Reservation.objects.get(pk=pk, user_id=user_id)
        res.status = 'CANCELLED'
        res.save()
    except Exception:
        pass
    return redirect('/reservations/')
