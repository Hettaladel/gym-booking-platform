import requests
import sys

# Test from inside reservations-service container
print("Testing connection to courses-service from reservations-service...")

# Test 1: Simple ping
url = "http://courses-service:8002/api/sessions/2/"
print(f"\nTest 1: GET {url}")
print("Without auth header (should get 401)...")

try:
    resp = requests.get(url, timeout=5)
    print(f"✓ Response: {resp.status_code}")
    print(f"  Body: {resp.text[:200]}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    sys.exit(1)

# Test 2: With auth header
print("\nTest 2: With Bearer token...")
token = sys.argv[1] if len(sys.argv) > 1 else "fake-token"
headers = {"Authorization": f"Bearer {token}"}

try:
    resp = requests.get(url, headers=headers, timeout=5)
    print(f"✓ Response: {resp.status_code}")
    print(f"  Body: {resp.text[:200]}")
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
    sys.exit(1)

print("\n✓ All tests passed!")
