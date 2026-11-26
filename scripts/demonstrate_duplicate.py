import requests
import sys

# Configuration
AUTH_URL = "http://localhost:8001/api/auth"
COURSES_URL = "http://localhost:8002/api/courses"
RESERVATIONS_URL = "http://localhost:8003/api/reservations"

print("=== TEST : PREVENTION DES DOUBLONS (Python) ===")

# 1. Login
try:
    print("1. Login Admin...", end=" ")
    resp = requests.post(f"{AUTH_URL}/login/", json={"username": "superadmin", "password": "admin123"})
    if resp.status_code != 200:
        print(f"FAIL: {resp.status_code} {resp.text}")
        sys.exit(1)
    token = resp.json()["access"]
    headers = {"Authorization": f"Bearer {token}"}
    print("OK")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    sys.exit(1)

# 2. Get Session
try:
    print("2. Recupération dernière séance...", end=" ")
    resp = requests.get(f"{COURSES_URL}/sessions/", headers=headers)
    sessions = resp.json()
    if not sessions:
        print("FAIL: Aucune séance trouvée.")
        sys.exit(1)
    # Get max ID
    last_session = max(sessions, key=lambda x: x['id'])
    session_id = last_session['id']
    print(f"OK (ID: {session_id})")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    sys.exit(1)

# 3. First Reservation
print("3. Première Réservation...", end=" ")
resp = requests.post(f"{RESERVATIONS_URL}/", json={"session_id": session_id}, headers=headers)
if resp.status_code == 201:
    print("REUSSIE (201 Created)")
elif resp.status_code == 400 and "Vous avez" in resp.text:
    print("DEJA FAITE (On continue)")
else:
    print(f"ERREUR INATTENDUE: {resp.status_code} {resp.text}")

# 4. SECOND Reservation (MUST FAIL)
print("4. Tentative de DOUBLON (Même ID)...")
resp = requests.post(f"{RESERVATIONS_URL}/", json={"session_id": session_id}, headers=headers)

if resp.status_code == 400:
    print("\n✅ SUCCES : Le système a bloqué le doublon !")
    print(f"   Message reçu : {resp.text}")
    print("   Code HTTP : 400 Bad Request")
else:
    print("\n⛔ ECHEC : Le doublon a été accepté ou autre erreur !")
    print(f"Code : {resp.status_code} - {resp.text}")

print("======================================")
