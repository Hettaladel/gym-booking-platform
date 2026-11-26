import pika
import json
import time

print("=" * 60)
print("TEST RABBITMQ - Envoi et Réception de Messages")
print("=" * 60)

# Configuration
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'notifications'

try:
    # Connexion à RabbitMQ
    print("\n1. Connexion à RabbitMQ...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBITMQ_HOST)
    )
    channel = connection.channel()
    print("✓ Connecté à RabbitMQ")
    
    # Déclarer la queue
    print("\n2. Déclaration de la queue 'notifications'...")
    channel.queue_declare(queue=QUEUE_NAME)
    print("✓ Queue déclarée")
    
    # Envoyer un message de test
    print("\n3. Envoi d'un message de test...")
    test_message = {
        'event_type': 'reservation_created',
        'user_id': 999,
        'session_id': 888,
        'message': 'Test message from test_rabbitmq_send.py',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(test_message)
    )
    print(f"✓ Message envoyé: {test_message}")
    
    # Vérifier le nombre de messages dans la queue
    print("\n4. Vérification de la queue...")
    method_frame = channel.queue_declare(queue=QUEUE_NAME, passive=True)
    message_count = method_frame.method.message_count
    print(f"✓ Nombre de messages dans la queue: {message_count}")
    
    # Fermer la connexion
    connection.close()
    print("\n✓ Test réussi! Le message a été envoyé à RabbitMQ.")
    print("\nVérifiez les logs du notification-service avec:")
    print("  docker logs notification-service --tail 20")
    
except Exception as e:
    print(f"\n✗ Erreur: {e}")

print("\n" + "=" * 60)
print("FIN DU TEST")
print("=" * 60)
