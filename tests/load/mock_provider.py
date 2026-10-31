"""Deterministic Open-Meteo-compatible provider used only by the load profile."""

from __future__ import annotations

import asyncio
import hashlib
import os
from datetime import date, timedelta

from fastapi import FastAPI, Query, Response

app = FastAPI(title="ClimaPrev load provider mock")


@app.get("/avisos/ativos")
async def alerts(response: Response) -> dict[str, object]:
    """Explicit synthetic empty coverage; never infer this from an HTTP error."""
    await _inject_delay(response)
    return {"hoje": [], "futuro": []}


@app.get("/v1/search")
async def search(response: Response, name: str = Query(min_length=1)) -> dict[str, object]:
    await _inject_delay(response)
    latitude, longitude = _coordinates_for_name(name)
    return {
        "results": [
            {
                "name": name.strip(),
                "latitude": latitude,
                "longitude": longitude,
                "timezone": "America/Sao_Paulo",
            }
        ]
    }


def _coordinates_for_name(name: str) -> tuple[float, float]:
    digest = hashlib.sha256(name.strip().encode("utf-8")).digest()
    latitude_bucket = int.from_bytes(digest[:4], byteorder="big") % 380_000
    longitude_bucket = int.from_bytes(digest[4:8], byteorder="big") % 400_000
    return (-33.0 + latitude_bucket / 10_000, -74.0 + longitude_bucket / 10_000)


@app.get("/v1/forecast")
async def forecast(response: Response, start_date: date, end_date: date) -> dict[str, object]:
    await _inject_delay(response)
    days = _days(start_date, end_date)
    return {
        "timezone": "America/Sao_Paulo",
        "daily": {
            "time": [day.isoformat() for day in days],
            "temperature_2m_min": [16.0 for _ in days],
            "temperature_2m_max": [28.0 for _ in days],
            "precipitation_sum": [4.0 for _ in days],
            "precipitation_probability_max": [35.0 for _ in days],
            "wind_speed_10m_max": [20.0 for _ in days],
            "wind_gusts_10m_max": [28.0 for _ in days],
            "weather_code": [3 for _ in days],
        },
        "hourly": {
            "time": [f"{day.isoformat()}T00:00" for day in days],
            "temperature_2m": [22.0 for _ in days],
            "relative_humidity_2m": [65.0 for _ in days],
            "precipitation": [2.0 for _ in days],
            "precipitation_probability": [35.0 for _ in days],
            "wind_speed_10m": [18.0 for _ in days],
            "wind_gusts_10m": [24.0 for _ in days],
        },
    }


def _days(start: date, end: date) -> tuple[date, ...]:
    return tuple(start + timedelta(days=index) for index in range((end - start).days + 1))


async def _inject_delay(response: Response) -> None:
    delay_milliseconds = _provider_delay_milliseconds()
    response.headers["X-Provider-Mock-Delay-Ms"] = str(delay_milliseconds)
    if delay_milliseconds:
        await asyncio.sleep(delay_milliseconds / 1000)


def _provider_delay_milliseconds() -> int:
    if os.getenv("CLIMAPREV_LOAD_SCENARIO", "warm_cache").strip().lower() not in {
        "slow_upstream",
        "lock_contention",
    }:
        return 0
    raw_delay = os.getenv("CLIMAPREV_PROVIDER_MOCK_DELAY_MS", "150")
    try:
        delay = int(raw_delay)
    except ValueError as error:
        raise ValueError("CLIMAPREV_PROVIDER_MOCK_DELAY_MS must be an integer") from error
    if delay < 0:
        raise ValueError("CLIMAPREV_PROVIDER_MOCK_DELAY_MS must not be negative")
    return delay
