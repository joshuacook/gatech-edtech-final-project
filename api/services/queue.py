import os

from fastapi import HTTPException
from redis import Redis
from rq import Queue


def get_redis_queue(logger):
    try:
        redis_conn = Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))
        return Queue("default", connection=redis_conn)
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise HTTPException(status_code=500, detail="Redis connection failed")
