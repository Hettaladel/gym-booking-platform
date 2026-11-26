import requests
import json

print("=" * 60)
print("TEST TRAEFIK - Vérification du routage")
print("=" * 60)

# Test 1: Dashboard Traefik
print("\n1. Test du Dashboard Traefik...")
try:
    response = requests.get("http://localhost:8080/api/overview")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Dashboard Traefik accessible")
        print(f"  Données: {json.dumps(data, indent=2)}")
    else:
        print(f"✗ Erreur: Status {response.status_code}")
except Exception as e:
    print(f"✗ Erreur de connexion: {e}")

# Test 2: Vérifier les routers
print("\n2. Vérification des routers Traefik...")
try:
    response = requests.get("http://localhost:8080/api/http/routers")
    if response.status_code == 200:
        routers = response.json()
        print(f"✓ Nombre de routers: {len(routers)}")
        for router in routers:
            print(f"\n  Router: {router['name']}")
            print(f"    Rule: {router.get('rule', 'N/A')}")
            print(f"    Service: {router.get('service', 'N/A')}")
            print(f"    Status: {router.get('status', 'N/A')}")
    else:
        print(f"✗ Erreur: Status {response.status_code}")
except Exception as e:
    print(f"✗ Erreur: {e}")

# Test 3: Vérifier les services
print("\n3. Vérification des services Traefik...")
try:
    response = requests.get("http://localhost:8080/api/http/services")
    if response.status_code == 200:
        services = response.json()
        print(f"✓ Nombre de services: {len(services)}")
        for service in services:
            print(f"\n  Service: {service['name']}")
            print(f"    Status: {service.get('status', 'N/A')}")
            if 'loadBalancer' in service:
                servers = service['loadBalancer'].get('servers', [])
                print(f"    Servers: {len(servers)}")
                for server in servers:
                    print(f"      - {server.get('url', 'N/A')}")
    else:
        print(f"✗ Erreur: Status {response.status_code}")
except Exception as e:
    print(f"✗ Erreur: {e}")

# Test 4: Test de routage via Traefik
print("\n4. Test de routage via Traefik (port 80)...")
endpoints = [
    ("Auth Service", "http://localhost/api/auth/health/"),
    ("Courses Service", "http://localhost/api/courses/health/"),
    ("Reservations Service", "http://localhost/api/reservations/health/")
]

for name, url in endpoints:
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✓ {name}: Accessible via Traefik")
        else:
            print(f"✗ {name}: Status {response.status_code}")
    except Exception as e:
        print(f"✗ {name}: Erreur - {e}")

# Test 5: Vérifier l'intégration Consul-Traefik
print("\n5. Vérification de l'intégration Consul-Traefik...")
try:
    response = requests.get("http://localhost:8080/api/providers")
    if response.status_code == 200:
        providers = response.json()
        print(f"✓ Providers configurés:")
        for provider_name, provider_data in providers.items():
            print(f"  - {provider_name}")
    else:
        print(f"✗ Erreur: Status {response.status_code}")
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\n" + "=" * 60)
print("FIN DU TEST TRAEFIK")
print("=" * 60)
