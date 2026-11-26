import requests
import sys

# Constants
AUTH_URL = "http://localhost:8001/api/auth"
COURSES_URL = "http://localhost:8002/api"

def seed():
    # 1. Login as Admin
    print("Logging in as admin...")
    resp = requests.post(f"{AUTH_URL}/login/", json={"username": "superadmin", "password": "admin123"})
    if resp.status_code != 200:
        print(f"Failed to login: {resp.text}")
        return
    token = resp.json()["access"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in successfully.")

    # 2. Create Course
    print("Creating 'Yoga' course...")
    course_data = {
        "title": "Yoga",
        "description": "Cours de Yoga pour débutants",
        "capacity": 10
    }
    # Check if exists first? Simplification: Just create (might duplicate if run twice, but DB was reset)
    resp = requests.post(f"{COURSES_URL}/courses/", json=course_data, headers=headers)
    if resp.status_code == 201:
        course = resp.json()
        print(f"Created course: {course}")
        course_id = course["id"]
    else:
        print(f"Failed to create course (maybe exists?): {resp.status_code} {resp.text}")
        # Try listing
        courses = requests.get(f"{COURSES_URL}/courses/", headers=headers).json()
        if courses:
            course_id = courses[0]["id"]
            print(f"Using existing course ID: {course_id}")
        else:
            return

    # 3. Create Session
    print(f"Creating session for course {course_id}...")
    session_data = {
        "course": course_id,
        "coach_id": 1, # Admin ID usually 1
        "start_datetime": "2025-12-25T10:00:00Z",
        "end_datetime": "2025-12-25T11:00:00Z",
        "capacity": 5
    }
    resp = requests.post(f"{COURSES_URL}/sessions/", json=session_data, headers=headers)
    if resp.status_code == 201:
        print(f"Created session: {resp.json()}")
    else:
        print(f"Failed to create session: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    try:
        seed()
    except Exception as e:
        print(f"Error: {e}")
