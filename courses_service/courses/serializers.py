from rest_framework import serializers
from .models import Course, Session


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'description']


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'course', 'coach_id', 'start_datetime', 'end_datetime', 'capacity']
