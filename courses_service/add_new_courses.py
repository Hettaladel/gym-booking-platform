import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from courses.models import Course

new_courses = [
    {'title': 'Cardio', 'description': 'High energy cardio workout'},
    {'title': 'HIIT', 'description': 'High Intensity Interval Training'},
    {'title': 'Pilates', 'description': 'Core strength and flexibility'},
    {'title': 'CrossFit', 'description': 'Functional movements performed at high intensity'}
]

for course_data in new_courses:
    course, created = Course.objects.get_or_create(
        title=course_data['title'],
        defaults={'description': course_data['description']}
    )
    if created:
        print(f"Created course: {course.title}")
    else:
        print(f"Course already exists: {course.title}")
