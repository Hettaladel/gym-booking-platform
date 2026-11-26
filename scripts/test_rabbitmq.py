import requests
import json

print("=" * 60)
print("TEST RABBITMQ - Vérification de l'infrastructure")
print("=" * 60)

# Test 1: RabbitMQ Management API
print("\n1. Test de l'API Management RabbitMQ...")
try:
    response = requests.get("http://localhost:15672/api/overview", auth=('guest', 'guest'))
    if response.status_code == 200:
        data = response.json()
        print(f"✓ RabbitMQ est accessible")
        print(f"  Version: {data.get('rabbitmq_version', 'N/A')}")
        print(f"  Erlang version: {data.get('erlang_version', 'N/A')}")
    else:
        print(f"✗ Erreur: Status {response.status_code}")
except Exception as e:
    print(f"✗ Erreur de connexion: {e}")

# Test 2: Vérifier les queues
print("\n2. Vérification des queues RabbitMQ...")
try:
    response = requests.get("http://localhost:15672/api/queues", auth=('guest', 'guest'))
    if response.status_code == 200:
        queues = response.json()
        print(f"✓ Nombre de queues: {len(queues)}")
        for queue in queues:
            print(f"  - {queue['name']}: {queue.get('messages', 0)} messages")
    else:
        print(f"✗ Erreur: Status {response.status_code}")
except Exception as e:
    print(f"✗ Erreur: {e}")

# Test 3: Vérifier les exchanges
print("\n3. Vérification des exchanges RabbitMQ...")
try:
    response = requests.get("http://localhost:15672/api/exchanges", auth=('guest', 'guest'))
    if response.status_code == 200:
        exchanges = response.json()
        print(f"✓ Nombre d'exchanges: {len(exchanges)}")
        for exchange in exchanges:
            if exchange['name']:  # Skip default exchange
                print(f"  - {exchange['name']} ({exchange['type']})")
    else:
        print(f"✗ Erreur: Status {response.status_code}")
except Exception as e:
    print(f"✗ Erreur: {e}")

# Test 4: Vérifier les connections
print("\n4. Vérification des connexions RabbitMQ...")
try:
    response = requests.get("http://localhost:15672/api/connections", auth=('guest', 'guest'))
    if response.status_code == 200:
        connections = response.json()
        print(f"✓ Nombre de connexions actives: {len(connections)}")
        for conn in connections:
            print(f"  - {conn.get('client_properties', {}).get('connection_name', 'Unknown')}")
    else:
        print(f"✗ Erreur: Status {response.status_code}")
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\n" + "=" * 60)
print("FIN DU TEST RABBITMQ")
print("=" * 60)
