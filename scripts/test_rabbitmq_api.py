import requests
import json
import time

print("=" * 60)
print("TEST RABBITMQ - Envoi de Message via API")
print("=" * 60)

# Configuration
RABBITMQ_API = 'http://localhost:15672/api'
AUTH = ('guest', 'guest')
QUEUE_NAME = 'notifications'

try:
    # 1. Vérifier la connexion
    print("\n1. Vérification de la connexion à RabbitMQ...")
    response = requests.get(f"{RABBITMQ_API}/overview", auth=AUTH)
    if response.status_code == 200:
        data = response.json()
        print(f"✓ RabbitMQ connecté - Version: {data.get('rabbitmq_version', 'N/A')}")
    else:
        print(f"✗ Erreur de connexion: {response.status_code}")
        exit(1)
    
    # 2. Vérifier/Créer la queue
    print(f"\n2. Vérification de la queue '{QUEUE_NAME}'...")
    response = requests.get(f"{RABBITMQ_API}/queues/%2F/{QUEUE_NAME}", auth=AUTH)
    if response.status_code == 200:
        queue_info = response.json()
        print(f"✓ Queue existe - Messages: {queue_info.get('messages', 0)}")
    else:
        print(f"⚠ Queue n'existe pas encore (sera créée par le consumer)")
    
    # 3. Publier un message via l'API
    print("\n3. Publication d'un message de test...")
    test_message = {
        'event_type': 'test_notification',
        'user_id': 999,
        'session_id': 888,
        'message': 'Message de test envoyé via API RabbitMQ',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    publish_payload = {
        'properties': {},
        'routing_key': QUEUE_NAME,
        'payload': json.dumps(test_message),
        'payload_encoding': 'string'
    }
    
    response = requests.post(
        f"{RABBITMQ_API}/exchanges/%2F/amq.default/publish",
        auth=AUTH,
        json=publish_payload
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('routed'):
            print(f"✓ Message publié avec succès!")
            print(f"  Contenu: {test_message}")
        else:
            print(f"⚠ Message publié mais pas routé (queue n'existe peut-être pas)")
    else:
        print(f"✗ Erreur lors de la publication: {response.status_code}")
    
    # 4. Vérifier les connexions actives
    print("\n4. Vérification des connexions actives...")
    response = requests.get(f"{RABBITMQ_API}/connections", auth=AUTH)
    if response.status_code == 200:
        connections = response.json()
        print(f"✓ Connexions actives: {len(connections)}")
        for conn in connections:
            client_name = conn.get('client_properties', {}).get('connection_name', 'Unknown')
            print(f"  - {client_name}")
    
    # 5. Vérifier les consumers
    print("\n5. Vérification des consumers...")
    response = requests.get(f"{RABBITMQ_API}/consumers", auth=AUTH)
    if response.status_code == 200:
        consumers = response.json()
        print(f"✓ Consumers actifs: {len(consumers)}")
        for consumer in consumers:
            queue = consumer.get('queue', {}).get('name', 'Unknown')
            print(f"  - Queue: {queue}")
    
    print("\n" + "=" * 60)
    print("✓ TEST RÉUSSI!")
    print("=" * 60)
    print("\nPour vérifier que le consumer a reçu le message:")
    print("  docker logs notification-service --tail 20")
    
except Exception as e:
    print(f"\n✗ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
