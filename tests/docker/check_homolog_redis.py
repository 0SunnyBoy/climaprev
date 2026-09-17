"""Run inside the homologation app; tests authentication without printing secrets."""

import asyncio
import urllib.request

from redis.asyncio import Redis
from redis.exceptions import AuthenticationError, NoPermissionError

from climaprev.application.ports import CacheEntry
from climaprev.config import Settings
from climaprev.infrastructure.cache.redis_cache import RedisCache
from climaprev.infrastructure.cache.redis_lock import RedisLock
from climaprev.infrastructure.rate_limit.provider_budget import ProviderBudget


async def check() -> None:
    settings = Settings()
    client = Redis.from_url(settings.redis_url, password=settings.redis_password)
    try:
        assert await client.ping() is True
        cache = RedisCache(client, environment="homolog-smoke")
        await cache.set("cache", CacheEntry(value={"fixture": 1}, is_stale=False), 30, 60)
        cached = await cache.get("cache")
        assert cached is not None and cached.value == {"fixture": 1}
        lock = RedisLock(client, environment="homolog-smoke")
        token = await lock.acquire("lock")
        assert token is not None
        assert await lock.refresh("lock", token) is True
        assert await lock.release("lock", token) is True
        await ProviderBudget(client, settings).consume("https://homolog-smoke.test/fixture")
        await client.set("climaprev:homolog-smoke", "fixture", ex=30)
        assert await client.get("climaprev:homolog-smoke") == b"fixture"
        denied = False
        try:
            await client.set("outside-namespace", "fixture")
        except NoPermissionError:
            denied = True
        assert denied
        await client.delete("climaprev:homolog-smoke")
    finally:
        await client.aclose()
    for password in (None, "wrong-synthetic-password"):
        unauthorized = Redis.from_url(settings.redis_url, password=password)
        rejected = False
        try:
            await unauthorized.ping()
        except AuthenticationError:
            rejected = True
        finally:
            await unauthorized.aclose()
        assert rejected
    print(
        "Redis: valid authentication works; absent/wrong authentication and foreign key rejected."
    )


if __name__ == "__main__":
    asyncio.run(check())
    with urllib.request.urlopen("http://app:8000/health/ready") as response:
        assert response.status == 200
    print("API readiness: internal HTTP 200.")
