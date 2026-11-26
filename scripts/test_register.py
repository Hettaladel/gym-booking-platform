import urllib.request
import json

url = "http://localhost/api/auth/register/"
payload = {
    "email": "etudiant1@example.com",
    "username": "etudiant1",
    "password": "TestPass123!",
    "password2": "TestPass123!",
    "role": "student"
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        print(f"Response: {response.read().decode('utf-8')}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
