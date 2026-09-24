"""Run inside the homologation app; tests authentication without printing secrets."""

import asyncio
import urllib.request
from uuid import uuid4

from redis.asyncio import Redis
from redis.exceptions import AuthenticationError, NoPermissionError

from climaprev.application.ports import CacheEntry
from climaprev.config import Settings
from climaprev.infrastructure.cache.redis_cache import RedisCache
from climaprev.infrastructure.cache.redis_lock import RedisLock
from climaprev.infrastructure.rate_limit.provider_budget import ProviderBudget
from climaprev.infrastructure.rate_limit.redis_rate_limiter import RedisRateLimiter


async def check() -> None:
    settings = Settings()
    fixture = f"security-smoke-{uuid4().hex}"
    key = f"climaprev:{settings.environment}:{fixture}"
    client = Redis.from_url(settings.redis_url, password=settings.redis_password)
    try:
        assert await client.ping() is True
        cache = RedisCache(client, environment=settings.environment)
        await cache.set(fixture, CacheEntry(value={"fixture": 1}, is_stale=False), 30, 60)
        cached = await cache.get(fixture)
        assert cached is not None and cached.value == {"fixture": 1}
        lock = RedisLock(client, environment=settings.environment)
        token = await lock.acquire(fixture)
        assert token is not None
        assert await lock.refresh(fixture, token) is True
        assert await lock.release(fixture, token) is True
        await ProviderBudget(client, settings).consume(f"https://{fixture}.test/fixture")
        decision = await RedisRateLimiter(
            client, environment=settings.environment, identity_key=settings.client_ip_hmac_key
        ).allow("198.51.100.7", limit=60, window_seconds=60, burst=10)
        assert decision.allowed
        await client.set(key, "fixture", ex=30)
        assert await client.get(key) == b"fixture"
        other = "test" if settings.environment != "test" else "production"
        for command in (
            ("SET", f"climaprev:{other}:{fixture}", "fixture", "EX", 10),
            ("EVAL", "return redis.call('GET', KEYS[1])", 1, f"climaprev:{other}:{fixture}"),
            ("CONFIG", "GET", "save"), ("ACL", "WHOAMI"), ("SCAN", "0"),
            ("HGETALL", key),
            # Invalid option guarantees no flush even if the ACL regresses.
            ("FLUSHALL", "__never_execute__"),
        ):
            denied = False
            try:
                await client.execute_command(*command)
            except NoPermissionError:
                denied = True
            assert denied, f"ACL did not reject {command[0]}"
        await client.delete(key)
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
    with urllib.request.urlopen("http://localhost:8000/health/ready") as response:
        assert response.status == 200
    print("API readiness: internal HTTP 200.")
