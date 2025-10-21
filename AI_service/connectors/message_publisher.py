# ai-service/connectors/message_publisher.py

import base64
import json
from datetime import datetime

import pika


def publish_violation(camera_id: str, violation_type: str, license_plate: str, image_bytes: bytes):
    """
    Đóng gói thông tin vi phạm và gửi vào RabbitMQ.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='violation_queue', durable=True)

        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        message = {
            "camera_id": camera_id,
            "violation_type": violation_type,
            "timestamp": datetime.utcnow().isoformat() + "Z", 
            "license_plate": license_plate,
            "image_base64": image_base64,
        }

        channel.basic_publish(
            exchange='',
            routing_key='violation_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  
            ))
        
        print(f" [x] Sent violation message for camera {camera_id}")
        connection.close()

    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")