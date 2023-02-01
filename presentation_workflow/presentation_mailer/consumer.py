import json
import pika
from pika.exceptions import AMQPConnectionError
import django
import os
import sys
import time
from django.core.mail import send_mail


sys.path.append("")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "presentation_mailer.settings")
django.setup()

while True:
    try:

        def process_approval(ch, method, properties, body):
            print("  Received %r" % body)

            data = json.loads(body)
            name = data["presenter_name"]
            title = data["title"]
            message = f"{name}, we're happy to tell you that your presentation {title} has been accepted"
            return send_mail(
                "Presentation Approved",
                message,
                "admin@conference.go",
                [data["presenter_email"]],
                fail_silently=False,
            )

        def process_rejection(ch, method, properties, body):
            print("  Received %r" % body)

            data = json.loads(body)
            name = data["presenter_name"]
            title = data["title"]
            message = f"{name}, we're happy to tell you that your presentation {title} has been rejected"
            return send_mail(
                "Presentation Rejected",
                message,
                "admin@conference.go",
                [data["presenter_email"]],
                fail_silently=False,
            )

        parameters = pika.ConnectionParameters(host="rabbitmq")
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue="presentation_approvals")
        channel.basic_consume(
            queue="presentation_approvals",
            on_message_callback=process_approval,
            auto_ack=True,
        )

        channel.queue_declare(queue="presentation_rejections")
        channel.basic_consume(
            queue="presentation_rejections",
            on_message_callback=process_rejection,
            auto_ack=True,
        )

        channel.start_consuming()
    except AMQPConnectionError:
        print("Could not connect to RabbitMQ")
        time.sleep(2.0)
