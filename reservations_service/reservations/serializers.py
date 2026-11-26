from rest_framework import serializers
from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "session_id", "user_id", "created_at", "status"]
        read_only_fields = ["id", "user_id", "created_at", "status"]
