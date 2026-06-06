import json
from typing import Any, Optional

from config.cache_conf import REDIS_DB, REDIS_DECODE_RESPONSES, REDIS_HOST, REDIS_PORT

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


redis_client = None

if redis:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=REDIS_DECODE_RESPONSES,
    )


def json_default(value):
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


async def get_cache(key: str) -> Optional[Any]:
    if not redis_client:
        return None

    try:
        value = await redis_client.get(key)
    except Exception:
        return None

    if not value:
        return None

    return json.loads(value)


async def set_cache(key: str, value: Any, expire: int = 3600):
    if not redis_client:
        return

    try:
        await redis_client.set(
            key,
            json.dumps(value, ensure_ascii=False, default=json_default),
            ex=expire,
        )
    except Exception:
        return


async def delete_cache(key: str):
    if not redis_client:
        return

    try:
        await redis_client.delete(key)
    except Exception:
        return


async def delete_pattern(pattern: str):
    if not redis_client:
        return

    try:
        keys = await redis_client.keys(pattern)
        if keys:
            await redis_client.delete(*keys)
    except Exception:
        return
