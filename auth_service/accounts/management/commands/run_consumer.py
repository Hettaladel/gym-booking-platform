from django.core.management.base import BaseCommand
import pika
import json
import os

class Command(BaseCommand):
    help = 'Starts the notification consumer'

    def handle(self, *args, **options):
        self.stdout.write('Starting Consumer...')
        RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
        
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue='notifications')

            def callback(ch, method, properties, body):
                event = json.loads(body)
                self.stdout.write(self.style.SUCCESS(f"Received event: {event}"))
                # Here we could send email...

            channel.basic_consume(queue='notifications', on_message_callback=callback, auto_ack=True)
            self.stdout.write(self.style.SUCCESS('Waiting for messages...'))
            channel.start_consuming()
        except Exception as e:
             self.stdout.write(self.style.ERROR(f"Error: {e}"))
