from django.db import models


class Reservation(models.Model):
    """
    Réservation d'une séance (session) d'un cours.
    On stocke seulement les IDs pour rester indépendant des autres microservices.
    """
    session_id = models.IntegerField()   # id de la Session dans courses_service
    user_id = models.IntegerField()      # id du membre dans auth_service
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="CONFIRMED")

    def __str__(self):
        return f"Reservation user={self.user_id} session={self.session_id} ({self.status})"
