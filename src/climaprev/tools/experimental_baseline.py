"""Archive the production forecast adapter and v1 evaluator, not a substitute model."""

import hashlib
import inspect
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from datetime import UTC, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from climaprev.config import Settings
from climaprev.domain.models import CanonicalLocation, DatePeriod
from climaprev.domain.risk_evaluator import RiskEvaluator
from climaprev.domain.risk_policy import RiskPolicy, policy_fingerprint
from climaprev.infrastructure.providers.open_meteo import OpenMeteoForecastClient
from climaprev.tools.experimental_archive import ForecastCapture, archive_forecast


async def collect_baseline(
    client: httpx.AsyncClient, location: CanonicalLocation, period: DatePeriod, directory: Path,
    *, before_send: Callable[[str], Awaitable[None]] | None = None,
) -> dict[str, Any]:
    now = datetime.now(UTC).date()
    if not now <= period.start <= period.end <= now + timedelta(days=6):
        raise ValueError("baseline must stay inside the current public UTC window")
    settings = Settings(additional_retries=0)
    if settings.forecast_base_url.rstrip("/") != "https://api.open-meteo.com":
        raise ValueError("baseline archive supports only the standard provider endpoint")
    forecast = await OpenMeteoForecastClient(
        client, settings, before_send=before_send,
    ).forecast(location, period)
    zone = ZoneInfo(forecast.location.timezone)
    policy = RiskPolicy()
    result = {
        "baseline_scope": "production_adapter_and_policy_not_public_cache_or_alerts",
        "forecast": asdict(forecast),
        "risk": asdict(RiskEvaluator().evaluate(forecast, policy)),
        "policy_sha256": policy_fingerprint(policy),
        "adapter_source_sha256": hashlib.sha256(
            Path(inspect.getfile(OpenMeteoForecastClient)).read_bytes(),
        ).hexdigest(),
        "model_identity": "unknown_auto_selection", "scientific_approval": False,
    }
    capture = ForecastCapture(
        "open-meteo", "unknown", "https://api.open-meteo.com/v1/forecast", forecast.location,
        forecast.fetched_at, datetime.combine(period.start, time.min, zone),
        datetime.combine(period.end + timedelta(days=1), time.min, zone), selection_mode="automatic",
    )
    return {"model": "operational-baseline", "archive": str(archive_forecast(directory, capture, result)),
            "collected_at": forecast.fetched_at.isoformat(), **result}
