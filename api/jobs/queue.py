# api/jobs/queue.py
import logging

from redis import Redis
from rq import Queue

logger = logging.getLogger(__name__)


def get_redis_queue():
    """Get Redis queue connection"""
    try:
        redis_conn = Redis.from_url("redis://redis:6379")
        return Queue("default", connection=redis_conn)
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise
