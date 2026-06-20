import redis.asyncio as redis
import json
from app.config import settings
from loguru import logger

class CacheService:

    def __init__(self):
        self.client = redis.from_url(settings.redis_url, decode_responses=True)

    async def get(self, key: str):
        try:
            val = await self.client.get(key)
            return json.loads(val) if val else None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None

    async def set(self, key: str, value, ttl: int = 60):
        try:
            await self.client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.warning(f"Cache set error: {e}")

    async def delete(self, key: str):
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except Exception:
            return False

cache = CacheService()
