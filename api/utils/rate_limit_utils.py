# api/utils/rate_limit.py
import asyncio
import logging
import time
from functools import wraps

from redis import Redis

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(
        self, redis_client, key_prefix="rate_limit", max_requests=3, per_seconds=1
    ):
        self.redis = redis_client
        self.key_prefix = key_prefix
        self.max_requests = max_requests
        self.per_seconds = per_seconds

    async def acquire(self):
        redis_key = f"{self.key_prefix}:claude"
        current_time = int(time.time())

        pipeline = self.redis.pipeline()
        pipeline.zremrangebyscore(redis_key, 0, current_time - self.per_seconds)
        pipeline.zcard(redis_key)
        pipeline.zadd(redis_key, {str(current_time): current_time})
        pipeline.expire(redis_key, self.per_seconds)

        _, current_requests, *_ = pipeline.execute()
        return current_requests < self.max_requests


def rate_limit(key="anthropic", max_requests=3, per_seconds=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            redis_client = Redis.from_url("redis://redis:6379")
            limiter = RateLimiter(
                redis_client, max_requests=max_requests, per_seconds=per_seconds
            )

            while not await limiter.acquire(key):
                await asyncio.sleep(1)

            return await func(*args, **kwargs)

        return wrapper

    return decorator
