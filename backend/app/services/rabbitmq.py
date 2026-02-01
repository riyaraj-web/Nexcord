import aio_pika
from app.core.config import settings
import json

class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
    
    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
            self.channel = await self.connection.channel()
            await self.channel.declare_queue("notifications", durable=True)
            await self.channel.declare_queue("analytics", durable=True)
        except Exception as e:
            print(f"RabbitMQ connection error: {e}")
    
    async def publish_notification(self, user_id: str, notification: dict):
        if not self.channel:
            await self.connect()
        
        try:
            message = aio_pika.Message(
                body=json.dumps({"user_id": user_id, **notification}).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            await self.channel.default_exchange.publish(
                message, routing_key="notifications"
            )
        except Exception as e:
            print(f"RabbitMQ publish error: {e}")
    
    async def publish_analytics_event(self, event: dict):
        if not self.channel:
            await self.connect()
        
        try:
            message = aio_pika.Message(
                body=json.dumps(event).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )
            await self.channel.default_exchange.publish(
                message, routing_key="analytics"
            )
        except Exception as e:
            print(f"RabbitMQ publish error: {e}")
    
    async def close(self):
        if self.connection:
            await self.connection.close()
