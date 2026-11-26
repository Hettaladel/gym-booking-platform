from django.db import models
from django.db.models import DateTimeField

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title


class Session(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sessions")
    coach_id = models.IntegerField()  # id du coach venant du microservice Auth
    start_datetime = models.DateTimeField()
    end_datetime = DateTimeField()
    capacity = models.IntegerField(default=20)

    def __str__(self):
        return f"{self.course.title} - {self.start_datetime}"
