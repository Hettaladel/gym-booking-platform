
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_or_update_user(username, email, password, role):
    try:
        user = User.objects.get(username=username)
        print(f"User {username} exists. Updating password and role...")
        user.set_password(password)
        user.email = email
        user.role = role
        user.save()
        print(f"User {username} updated.")
    except User.DoesNotExist:
        print(f"Creating user {username} ({role})...")
        user = User.objects.create_user(username=username, email=email, password=password)
        user.role = role
        user.save()
        print(f"User {username} created.")

if __name__ == '__main__':
    print("--- Restoring/Updating Users ---")
    create_or_update_user('admin', 'admin@wams.gym', 'admin123', 'ADMIN')
    create_or_update_user('coach1', 'coach1@wams.gym', 'password123', 'COACH')
    create_or_update_user('member1', 'member1@wams.gym', 'password123', 'MEMBER')
    print("--- Done ---")
