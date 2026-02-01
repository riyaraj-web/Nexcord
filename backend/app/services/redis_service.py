import redis.asyncio as redis
from app.core.config import settings
import json

class RedisService:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
    
    async def set_user_status(self, user_id: str, status: str):
        await self.redis.hset(f"user:{user_id}", "status", status)
        await self.redis.hset(f"user:{user_id}", "last_seen", str(int(redis.time.time())))
    
    async def get_user_status(self, user_id: str) -> str:
        return await self.redis.hget(f"user:{user_id}", "status") or "offline"
    
    async def add_to_channel(self, channel_id: str, user_id: str):
        await self.redis.sadd(f"channel:{channel_id}:members", user_id)
    
    async def remove_from_channel(self, channel_id: str, user_id: str):
        await self.redis.srem(f"channel:{channel_id}:members", user_id)
    
    async def get_channel_members(self, channel_id: str) -> list:
        members = await self.redis.smembers(f"channel:{channel_id}:members")
        return list(members)
    
    async def cache_message(self, message_id: str, message_data: dict, ttl: int = 3600):
        await self.redis.setex(f"message:{message_id}", ttl, json.dumps(message_data))
    
    async def get_cached_message(self, message_id: str) -> dict:
        data = await self.redis.get(f"message:{message_id}")
        return json.loads(data) if data else None
