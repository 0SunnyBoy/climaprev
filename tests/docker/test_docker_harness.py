import os
from urllib.parse import urlparse

from redis.asyncio import Redis


async def test_redis_is_reachable_by_service_hostname() -> None:
    redis_url = os.environ["REDIS_URL"]
    assert urlparse(redis_url).hostname == "redis"

    client = Redis.from_url(redis_url)
    try:
        assert await client.ping() is True
    finally:
        await client.aclose()
