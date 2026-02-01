import redis.asyncio as redis
from app.core.config import settings
from datetime import datetime

class RateLimiter:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.max_messages = settings.RATE_LIMIT_MESSAGES
        self.window = settings.RATE_LIMIT_WINDOW
    
    async def check_rate_limit(self, user_id: str) -> bool:
        key = f"rate_limit:{user_id}"
        current_time = int(datetime.utcnow().timestamp())
        
        pipe = self.redis.pipeline()
        pipe.zadd(key, {str(current_time): current_time})
        pipe.zremrangebyscore(key, 0, current_time - self.window)
        pipe.zcard(key)
        pipe.expire(key, self.window)
        
        results = await pipe.execute()
        message_count = results[2]
        
        return message_count <= self.max_messages
