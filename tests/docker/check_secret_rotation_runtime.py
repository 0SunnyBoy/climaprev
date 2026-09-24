"""Verify a synthetic rotation in the running homolog stack without printing secrets."""

import argparse
import subprocess
from pathlib import Path
from uuid import uuid4

APP = "climaprev-homolog-app-1"

OLD_AUTH = """
import asyncio
import sys
from redis.asyncio import Redis
from redis.exceptions import AuthenticationError
from climaprev.config import Settings

async def main():
    settings = Settings()
    client = Redis.from_url(settings.redis_url, password=sys.stdin.read().strip())
    try:
        try:
            await client.ping()
        except AuthenticationError:
            print('old_rejected')
            return
        raise AssertionError('old credential still works')
    finally:
        await client.aclose()

asyncio.run(main())
"""

SHARED_QUOTA = """
import asyncio
import sys
from redis.asyncio import Redis
from climaprev.config import Settings
from climaprev.infrastructure.rate_limit.redis_rate_limiter import RedisRateLimiter

async def main():
    settings = Settings()
    client = Redis.from_url(settings.redis_url, password=settings.redis_password)
    try:
        limiter = RedisRateLimiter(
            client, environment=settings.environment, identity_key=settings.client_ip_hmac_key
        )
        decision = await limiter.allow(sys.argv[1], limit=1, window_seconds=3600, burst=1)
        print('allowed' if decision.allowed else 'denied')
    finally:
        await client.aclose()

asyncio.run(main())
"""


def execute(code: str, *, input_text: str | None = None, identity: str | None = None) -> str:
    command = ["docker", "exec", "-i", APP, "python", "-c", code]
    if identity is not None:
        command.append(identity)
    result = subprocess.run(
        command,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, "Synthetic rotation probe failed"
    return result.stdout.strip()


def check(old_password_file: Path) -> None:
    old_password = old_password_file.read_text(encoding="utf-8")
    assert old_password.strip()
    assert execute(OLD_AUTH, input_text=old_password) == "old_rejected"
    identity = f"2001:db8::{uuid4().hex[:8]}"
    assert execute(SHARED_QUOTA, identity=identity) == "allowed"
    assert execute(SHARED_QUOTA, identity=identity) == "denied"
    print("Synthetic rotation: old password rejected; new HMAC quota shared across workers.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--old-password-file", type=Path, required=True)
    check(parser.parse_args().old_password_file)
