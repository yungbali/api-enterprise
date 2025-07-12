"""
Redis Configuration
"""
import redis.asyncio as redis
from typing import Optional
import json

from app.core.config import settings


class RedisClient:
    """Redis client wrapper."""
    
    def __init__(self, url: str):
        self.url = url
        self._client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        if not self._client:
            self._client = redis.from_url(self.url, encoding="utf-8", decode_responses=True)
        return self._client
    
    async def close(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
    
    async def ping(self) -> bool:
        """Test Redis connection."""
        client = await self.connect()
        return await client.ping()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        client = await self.connect()
        return await client.get(key)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set value in Redis."""
        client = await self.connect()
        return await client.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> int:
        """Delete key from Redis."""
        client = await self.connect()
        return await client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        client = await self.connect()
        return await client.exists(key)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        client = await self.connect()
        return await client.expire(key, seconds)
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get field from hash."""
        client = await self.connect()
        return await client.hget(name, key)
    
    async def hset(self, name: str, key: str, value: str) -> int:
        """Set field in hash."""
        client = await self.connect()
        return await client.hset(name, key, value)
    
    async def hdel(self, name: str, *keys: str) -> int:
        """Delete fields from hash."""
        client = await self.connect()
        return await client.hdel(name, *keys)
    
    async def hgetall(self, name: str) -> dict:
        """Get all fields from hash."""
        client = await self.connect()
        return await client.hgetall(name)
    
    async def lpush(self, name: str, *values: str) -> int:
        """Push values to list."""
        client = await self.connect()
        return await client.lpush(name, *values)
    
    async def rpop(self, name: str) -> Optional[str]:
        """Pop value from list."""
        client = await self.connect()
        return await client.rpop(name)
    
    async def llen(self, name: str) -> int:
        """Get list length."""
        client = await self.connect()
        return await client.llen(name)
    
    async def set_json(self, key: str, value: dict, ex: Optional[int] = None) -> bool:
        """Set JSON value in Redis."""
        json_value = json.dumps(value)
        return await self.set(key, json_value, ex=ex)
    
    async def get_json(self, key: str) -> Optional[dict]:
        """Get JSON value from Redis."""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment key value."""
        client = await self.connect()
        return await client.incr(key, amount)
    
    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement key value."""
        client = await self.connect()
        return await client.decr(key, amount)


# Create Redis client instance
redis_client = RedisClient(settings.REDIS_URL)


# Cache decorator
def cache(ttl: int = 300):
    """Cache decorator for functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await redis_client.get_json(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            if result is not None:
                await redis_client.set_json(cache_key, result, ex=ttl)
            
            return result
        return wrapper
    return decorator
