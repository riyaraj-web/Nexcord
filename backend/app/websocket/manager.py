from fastapi import WebSocket
from typing import Dict
from datetime import datetime
from app.services.redis_service import RedisService
from app.services.ai_moderation import AIModerationService
from app.services.rate_limiter import RateLimiter

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.redis_service = RedisService()
        self.ai_moderation = AIModerationService()
        self.rate_limiter = RateLimiter()
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        await self.redis_service.set_user_status(user_id, "online")
        await self.broadcast_presence(user_id, "online")
    
    async def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        await self.redis_service.set_user_status(user_id, "offline")
        await self.broadcast_presence(user_id, "offline")
    
    async def handle_message(self, user_id: str, data: dict):
        message_type = data.get("type")
        
        if message_type == "message":
            if not await self.rate_limiter.check_rate_limit(user_id):
                await self.send_personal_message(user_id, {
                    "type": "error",
                    "message": "Rate limit exceeded (100 messages/min)"
                })
                return
            
            content = data.get("content", "")
            moderation_result = await self.ai_moderation.moderate_content(content)
            
            if moderation_result["is_toxic"]:
                await self.send_personal_message(user_id, {
                    "type": "moderation_warning",
                    "message": "Your message was flagged by AI moderation",
                    "categories": moderation_result["categories"]
                })
                return
            
            await self.broadcast_to_channel(data.get("channel_id"), {
                "type": "message",
                "user_id": user_id,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        elif message_type == "typing":
            await self.broadcast_to_channel(data.get("channel_id"), {
                "type": "typing",
                "user_id": user_id
            }, exclude_user=user_id)
        
        elif message_type == "read_receipt":
            await self.broadcast_to_channel(data.get("channel_id"), {
                "type": "read_receipt",
                "user_id": user_id,
                "message_id": data.get("message_id")
            })
    
    async def send_personal_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)
    
    async def broadcast_to_channel(self, channel_id: str, message: dict, exclude_user: str = None):
        channel_members = await self.redis_service.get_channel_members(channel_id)
        for user_id in channel_members:
            if user_id != exclude_user and user_id in self.active_connections:
                await self.active_connections[user_id].send_json(message)
    
    async def broadcast_presence(self, user_id: str, status: str):
        message = {
            "type": "presence",
            "user_id": user_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        for connection in self.active_connections.values():
            await connection.send_json(message)
