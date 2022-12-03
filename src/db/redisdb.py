from redis import asyncio as aioredis

from core.config import app_settings

connection = aioredis.Redis(
    host=app_settings.redis_host,
    port=app_settings.redis_port,
    decode_responses=True,
)
