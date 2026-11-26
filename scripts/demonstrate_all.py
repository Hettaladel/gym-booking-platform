import requests
import json
import time

# === COLORS ===
GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# === CONFIG ===
BASE_URL = "http://localhost"
AUTH_URL = f"{BASE_URL}/api/auth" # /api/auth/register, /api/auth/login
USER_URL = f"{BASE_URL}/api/users" # /api/users/me
COURSES_URL = f"{BASE_URL}/api/courses" # /api/courses/courses, /api/courses/sessions/
RESERVATIONS_URL = f"{BASE_URL}/api/reservations"

def print_step(msg):
    print(f"\n{CYAN}>>> {msg}{RESET}")

def print_ok(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_fail(msg):
    print(f"{RED}✗ {msg}{RESET}")

def demo():
    print(f"{YELLOW}DEMARRAGE DU TEST COMPLET DU SYSTEME{RESET}")
    print("====================================")

    # 1. REGISTER
    print_step("1. Inscription d'un nouvel utilisateur")
    username = f"demo_user_{int(time.time())}"
    user_data = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "Password123!",
        "password2": "Password123!"
    }
    try:
        resp = requests.post(f"{AUTH_URL}/register/", json=user_data)
        if resp.status_code == 201:
            print_ok(f"Utilisateur créé : {username}")
        else:
            print_fail(f"Erreur Inscription : {resp.text}")
            return
    except Exception as e:
        print_fail(f"Erreur Connection : {e}")
        return

    # 2. LOGIN
    print_step("2. Connexion (Récupération du Token)")
    try:
        resp = requests.post(f"{AUTH_URL}/login/", json={"username": username, "password": "Password123!"})
        if resp.status_code == 200:
            token = resp.json()["access"]
            print_ok("Token d'accès récupéré")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print_fail(f"Erreur Login : {resp.text}")
            return
    except Exception as e:
        print_fail(f"Erreur Connection : {e}")
        return

    # 3. PROFILE
    print_step("3. Vérification du Profil")
    try:
        resp = requests.get(f"{USER_URL}/me/", headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            print_ok(f"Bienvenue, {data['username']} (ID: {data['id']})")
        else:
            print_fail(f"Erreur Profil : {resp.status_code} {resp.text}")
    except Exception as e:
        print_fail(f"Erreur Connection : {e}")

    # 4. LIST COURSES & SESSIONS
    print_step("4. Consultation du Planning")
    session_id = None
    try:
        # Check Courses
        resp = requests.get(f"{COURSES_URL}/courses/", headers=headers)
        if resp.status_code == 200:
            count = len(resp.json())
            print_ok(f"{count} Cours disponibles.")
        else:
            print_fail(f"Erreur Cours : {resp.status_code}")

        # Check Sessions
        resp = requests.get(f"{COURSES_URL}/sessions/", headers=headers)
        if resp.status_code == 200:
            sessions = resp.json()
            count_s = len(sessions)
            print_ok(f"{count_s} Séances disponibles.")
            if count_s > 0:
                # Take the LAST session (most likely to be valid)
                target_session = max(sessions, key=lambda x: x['id'])
                session_id = target_session['id']
                print(f"   -> Cible pour réservation : Séance ID {session_id} ({target_session['start_datetime']})")
            else:
                print_fail("Aucune séance pour tester la réservation.")
                return
        else:
            print_fail(f"Erreur Séances : {resp.status_code}")
            return
    except Exception as e:
        print_fail(f"Erreur Connection : {e}")
        return

    # 5. CREATE RESERVATION
    print_step("5. Réservation d'une place")
    try:
        resp = requests.post(f"{RESERVATIONS_URL}/", json={"session_id": session_id}, headers=headers)
        if resp.status_code == 201:
            res_data = resp.json()
            res_id = res_data['id']
            print_ok(f"Réservation réussie ! (ID: {res_id}, Statut: {res_data['status']})")
        else:
            print_fail(f"Echec réservation : {resp.status_code} {resp.text}")
            res_id = None
    except Exception as e:
        print_fail(f"Erreur Connection : {e}")

    # 6. DUPLICATE CHECK
    print_step("6. Test de Sécurité (Tentative de Doublon)")
    try:
        resp = requests.post(f"{RESERVATIONS_URL}/", json={"session_id": session_id}, headers=headers)
        if resp.status_code == 400:
            print_ok(f"Le système a bien BLOQUÉ le doublon.")
            print(f"   Message : {resp.text}")
        elif resp.status_code == 201:
            print_fail("GRAVE : Le système a accepté le doublon !")
        else:
            print_fail(f"Réponse inattendue : {resp.status_code} {resp.text}")
    except Exception as e:
        print_fail(f"Erreur Connection : {e}")

    # 7. CANCEL
    print_step("7. Annulation de la réservation")
    if res_id:
        try:
            resp = requests.delete(f"{RESERVATIONS_URL}/{res_id}/", headers=headers)
            if resp.status_code == 200:
                 print_ok("Réservation annulée avec succès.")
                 print(f"   Statut : {resp.json().get('status')}")
            else:
                 print_fail(f"Echec annulation : {resp.status_code} {resp.text}")
        except Exception as e:
            print_fail(f"Erreur Connection : {e}")
    else:
        print("   (Pas de réservation à annuler)")

    print("\n====================================")
    print(f"{GREEN}TEST TERMINE{RESET}")

if __name__ == "__main__":
    demo()
