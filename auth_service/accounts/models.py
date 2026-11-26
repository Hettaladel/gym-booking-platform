from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        MEMBER = 'MEMBER', 'Membre'
        COACH = 'COACH', 'Coach'
        ADMIN = 'ADMIN', 'Administrateur'

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.MEMBER,
    )

    # Tu peux ajouter d’autres champs si besoin, ex:
    # phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
