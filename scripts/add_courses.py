import requests
import sys

# Constants
# We use the internal Docker network URLs or mapped localhost ports.
# Since we are running this from the HOST machine, we use the ports mapped in docker-compose.
AUTH_URL = "http://localhost:8001/api/auth"
COURSES_URL = "http://localhost:8002/api"

NEW_COURSES = [
    {"title": "CrossFit", "description": "High intensity interval training.", "capacity": 12},
    {"title": "Pilates", "description": "Core strength and flexibility.", "capacity": 8},
    {"title": "Boxing", "description": "Learn to box with professional coaches.", "capacity": 15},
    {"title": "Zumba", "description": "Dance fitness party.", "capacity": 20},
]

def add_courses():
    # 1. Login as Superadmin to get a token
    print("Logging in as superadmin...")
    try:
        resp = requests.post(f"{AUTH_URL}/login/", json={"username": "superadmin", "password": "admin123"})
        if resp.status_code != 200:
            print(f"Failed to login: {resp.status_code} {resp.text}")
            # Try creating superadmin if not exists? No, assuming it exists from setup.
            # If not, we might need to use the 'coach1' user created in previous steps if they have admin rights,
            # but usually only ADMIN role can create course TYPES, while COACH creates SESSIONS.
            # Let's try 'coach3' which we just fixed, assuming coaches can create courses? 
            # Looking at code, usually Admin creates Courses, Coach creates Sessions.
            # Let's try to use the 'superadmin' which should have been created by initial seeds.
            return
            
        token = resp.json()["access"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Logged in successfully.")

        # 2. Loop through courses and create them
        for course in NEW_COURSES:
            print(f"Adding {course['title']}...")
            r = requests.post(f"{COURSES_URL}/courses/", json=course, headers=headers)
            if r.status_code == 201:
                print(f"  [SUCCESS] Created {course['title']}")
            elif r.status_code == 400:
                print(f"  [INFO] {course['title']} might already exist.")
            else:
                print(f"  [ERROR] Failed to create {course['title']}: {r.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_courses()
