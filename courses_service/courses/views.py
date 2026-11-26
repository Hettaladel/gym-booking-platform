from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.dateparse import parse_date

from .models import Course, Session
from .serializers import CourseSerializer, SessionSerializer
from .permissions import IsAdminOrReadOnly, IsCoachOrAdmin

# --- Frontend Imports ---
from django.shortcuts import render, redirect
import requests
# -------------------------


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsCoachOrAdmin]

    def get_queryset(self):
        qs = super().get_queryset()

        date_str = self.request.query_params.get("date")
        coach_id = self.request.query_params.get("coach_id")
        course_id = self.request.query_params.get("course_id")

        if date_str:
            d = parse_date(date_str)
            if d:
                qs = qs.filter(start_datetime__date=d)

        if coach_id:
            qs = qs.filter(coach_id=coach_id)

        if course_id:
            qs = qs.filter(course_id=course_id)

        return qs

    @action(detail=False, methods=["get"])
    def my_sessions(self, request):
        """
        GET /api/sessions/my_sessions/
        Pour un coach : ses propres séances (coach_id = user.id)
        """
        qs = self.get_queryset().filter(coach_id=request.user.id)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

# --- Frontend Views ---

def home_view(request):
    user = getattr(request, 'user', None)
    role = getattr(user, 'role', 'MEMBER')
    
    if role == 'ADMIN':
        return redirect('http://localhost:8001/gym-admin/dashboard/')

    # Determine sessions based on role
    if role == 'COACH':
        user_id = getattr(user, 'id', None)
        sessions = Session.objects.filter(coach_id=user_id).order_by('-start_datetime') if user_id else []
        template_name = 'courses/home_coach.html'
    else:
        # MEMBER gets all upcoming sessions
        sessions = Session.objects.all().order_by('start_datetime')
        template_name = 'courses/home.html'
    
    # Enrich sessions with reservation data and images
    token = request.COOKIES.get('access_token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    
    # 1. Fetch Coach Details
    coach_ids = list(set([s.coach_id for s in sessions]))
    coach_map = {}
    if coach_ids:
        try:
            ids_str = ','.join(map(str, coach_ids))
            users_url = f"http://auth-service:8001/api/users/?ids={ids_str}"
            users_resp = requests.get(users_url, headers=headers, timeout=1)
            if users_resp.status_code == 200:
                users = users_resp.json()
                # Handle pagination results if present
                if isinstance(users, dict) and 'results' in users:
                    users = users['results']
                coach_map = {u['id']: u for u in users}
        except Exception as e:
            print(f"Error fetching coaches: {e}", flush=True)

    enriched_sessions = []
    for session in sessions:
        # Get Coach Name
        c_data = coach_map.get(session.coach_id, {})
        c_name = c_data.get('username', f"Coach {session.coach_id}")
        
        session_data = {
            'session': session,
            'coach_name': c_name,
            'reservations': []
        }
        
        # Map Course Images (Local Files)
        ct = session.course.title.lower()
        # Default placeholder 
        default_img = '/static/courses/images/yoga.png' 
        
        img_map = {
            'yoga': '/static/courses/images/yoga.png',
            'hiit': '/static/courses/images/hiit.png',
            'pilates': '/static/courses/images/pilates.png',
            'crossfit': '/static/courses/images/crossfit.png',
            'boxing': '/static/courses/images/boxing.png',
            'cardio': '/static/courses/images/cardio.png',
            'strength': '/static/courses/images/strength.png'
        }
        session_data['image_url'] = img_map.get(ct, default_img)
        
        try:
            # Fetch reservations for this session (Needed for both to show availability/bookings)
            res_url = f"http://reservations-service:8003/api/reservations/reservations/?session_id={session.id}"
            res_resp = requests.get(res_url, headers=headers, timeout=1)
            
            if res_resp.status_code == 200:
                reservations = res_resp.json()
                if isinstance(reservations, dict) and 'results' in reservations:
                    reservations = reservations['results']
                
                # Calculate available spots for Members
                confirmed_count = len([r for r in reservations if r.get('status') == 'CONFIRMED'])
                session_data['available_spots'] = session.capacity - confirmed_count
                
                # Check if current user has reserved (for Members)
                if role != 'COACH':
                    user_id = getattr(user, 'id', None)
                    session_data['is_reserved'] = any(r.get('user_id') == user_id and r.get('status') == 'CONFIRMED' for r in reservations)

                # For Coaches, we need full user details
                if role == 'COACH':
                    # Get unique confirmed user IDs
                    user_ids = list(set([r['user_id'] for r in reservations if isinstance(r, dict) and r.get('status') == 'CONFIRMED']))
                    
                    if user_ids:
                        user_ids_str = ','.join(map(str, user_ids))
                        users_url = f"http://auth-service:8001/api/users/?ids={user_ids_str}"
                        users_resp = requests.get(users_url, headers=headers, timeout=1)
                        
                        if users_resp.status_code == 200:
                            users = users_resp.json()
                            user_map = {u['id']: u for u in users}
                            
                            seen_users = set()
                            for reservation in reservations:
                                if reservation.get('status') == 'CONFIRMED':
                                    uid = reservation.get('user_id')
                                    if uid and uid not in seen_users:
                                        seen_users.add(uid)
                                        user_data = user_map.get(uid, {})
                                        session_data['reservations'].append({
                                            'id': reservation['id'],
                                            'username': user_data.get('username', 'Unknown'),
                                            'first_name': user_data.get('first_name', ''),
                                            'last_name': user_data.get('last_name', ''),
                                            'email': user_data.get('email', 'N/A')
                                        })
        except Exception as e:
            print(f"Error fetching reservations for session {session.id}: {e}", flush=True)
        
        enriched_sessions.append(session_data)
        
    return render(request, template_name, {'sessions': enriched_sessions})


def create_session_view(request):
    user = getattr(request, 'user', None)
    role = getattr(user, 'role', 'MEMBER')
    
    if role == 'MEMBER':
        return redirect('/') 

    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        start = request.POST.get('start_datetime')
        end = request.POST.get('end_datetime')
        cap = request.POST.get('capacity')
        
        try:
            course = Course.objects.get(pk=course_id)
            Session.objects.create(
                course=course,
                coach_id=user.id,
                start_datetime=start,
                end_datetime=end,
                capacity=cap
            )
            return redirect('/')
        except Exception as e:
            courses = Course.objects.all()
            return render(request, 'courses/create_session.html', {'courses': courses, 'error': str(e)})

    # GET
    courses = Course.objects.all()
    return render(request, 'courses/create_session.html', {'courses': courses})


def session_details_view(request, session_id):
    """
    View for coaches to see detailed information about a session
    including all member reservations
    """
    user = getattr(request, 'user', None)
    role = getattr(user, 'role', 'MEMBER')
    
    # Only coaches and admins can view session details
    if role == 'MEMBER':
        return redirect('/')
    
    try:
        session = Session.objects.get(pk=session_id)
        
        # Check if coach owns this session (admins can view all)
        if role == 'COACH' and session.coach_id != user.id:
            return redirect('/')
        
        # Fetch reservations for this session
        token = request.COOKIES.get('access_token')
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        
        reservations = []
        try:
            # Fetch reservations from reservations service
            res_url = f"http://reservations-service:8003/api/reservations/reservations/?session_id={session.id}"
            res_resp = requests.get(res_url, headers=headers, timeout=1)
            
            if res_resp.status_code == 200:
                reservations_data = res_resp.json()
                
                if isinstance(reservations_data, dict) and 'results' in reservations_data:
                    reservations_data = reservations_data['results']
                
                # Get unique user IDs
                user_ids = list(set([r['user_id'] for r in reservations_data if isinstance(r, dict) and r.get('status') == 'CONFIRMED']))
                
                if user_ids:
                    # Fetch user details
                    user_ids_str = ','.join(map(str, user_ids))
                    users_url = f"http://auth-service:8001/api/users/?ids={user_ids_str}"
                    users_resp = requests.get(users_url, headers=headers, timeout=1)
                    
                    if users_resp.status_code == 200:
                        users = users_resp.json()
                        if isinstance(users, dict) and 'results' in users:
                             users = users['results']
                        
                        # Create a mapping of user_id to user data
                        user_map = {u['id']: u for u in users}
                        
                        # Enrich reservations with user data
                        for reservation in reservations_data:
                            if reservation.get('status') == 'CONFIRMED':
                                user_data = user_map.get(reservation['user_id'], {})
                                reservations.append({
                                    'id': reservation['id'],
                                    'username': user_data.get('username', 'Unknown'),
                                    'email': user_data.get('email', 'N/A'),
                                    'first_name': user_data.get('first_name', ''),
                                    'last_name': user_data.get('last_name', ''),
                                    'created_at': reservation.get('created_at', ''),
                                })
        except Exception as e:
            print(f"Error fetching reservations: {e}", flush=True)
        
        context = {
            'session': session,
            'reservations': reservations,
            'reservation_count': len(reservations)
        }
        
        return render(request, 'courses/session_details.html', context)
        
    except Session.DoesNotExist:
        return redirect('/')


def coach_session_update_view(request, session_id):
    """
    View for coach to update session details (capacity, times)
    """
    user = getattr(request, 'user', None)
    role = getattr(user, 'role', 'MEMBER')
    
    if role != 'COACH':
        return redirect('/')
        
    try:
        session = Session.objects.get(pk=session_id)
        # Verify ownership
        if session.coach_id != user.id:
            return redirect('/')
            
        if request.method == 'POST':
            # Manual form handling for simplicity
            start = request.POST.get('start_datetime')
            end = request.POST.get('end_datetime')
            capacity = request.POST.get('capacity')
            
            if start and end and capacity:
                session.start_datetime = start
                session.end_datetime = end
                session.capacity = capacity
                session.save()
                return redirect('session_details', session_id=session.id)
                
        return render(request, 'courses/session_form.html', {'session': session})
        
    except Session.DoesNotExist:
        return redirect('/')


def coach_session_delete_view(request, session_id):
    """
    View for coach to delete a session
    """
    user = getattr(request, 'user', None)
    role = getattr(user, 'role', 'MEMBER')
    
    if role != 'COACH':
        return redirect('/')
        
    try:
        session = Session.objects.get(pk=session_id)
        # Verify ownership
        if session.coach_id != user.id:
            return redirect('/')
            
        if request.method == 'POST':
            session.delete()
            return redirect('/')
            
        return render(request, 'courses/session_confirm_delete.html', {'session': session})
        
    except Session.DoesNotExist:
        return redirect('/')


def admin_session_list_view(request):
    """
    View for admin to see all sessions in a table.
    """
    user = getattr(request, 'user', None)
    role = getattr(user, 'role', 'MEMBER')
    
    if role != 'ADMIN':
        return redirect('/')
    
    # Fetch all sessions
    sessions = Session.objects.all().order_by('-start_datetime')
    
    # 1. Collect coach types
    coach_ids = list(set([s.coach_id for s in sessions]))
    
    # 2. Fetch coach details from Auth Service
    coach_map = {}
    if coach_ids:
        token = request.COOKIES.get('access_token')
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        try:
            ids_str = ','.join(map(str, coach_ids))
            users_url = f"http://auth-service:8001/api/users/?ids={ids_str}"
            users_resp = requests.get(users_url, headers=headers, timeout=1)
            if users_resp.status_code == 200:
                users = users_resp.json()
                coach_map = {u['id']: u for u in users}
        except Exception as e:
            print(f"Error fetching coaches: {e}", flush=True)

    # 3. Enrich
    enriched_sessions = []
    for s in sessions:
        coach_data = coach_map.get(s.coach_id, {})
        enriched_sessions.append({
            'session': s,
            'coach_name': coach_data.get('username', f"Coach {s.coach_id}"),
            'coach_email': coach_data.get('email', ''),
        })

    return render(request, 'courses/admin_session_list.html', {'sessions': enriched_sessions})

