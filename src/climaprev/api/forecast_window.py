"""Public forecast eligibility is a seven-date UTC window, not historical access."""

from datetime import UTC, date, datetime, timedelta

from climaprev.api.errors import ApplicationError


def utc_today() -> date:
    return datetime.now(UTC).date()


def forecast_window(now: datetime, *, horizon_days: int = 7) -> tuple[date, date]:
    if isinstance(horizon_days, bool) or not 1 <= horizon_days <= 16:
        raise ValueError("unsupported forecast horizon")
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("forecast clock must be timezone aware")
    first = now.astimezone(UTC).date()
    return first, first + timedelta(days=horizon_days - 1)


def validate_public_period(start: date, end: date) -> None:
    first = utc_today()
    last = first + timedelta(days=6)
    if not first <= start <= end <= last:
        raise ApplicationError(
            "INVALID_PERIOD", f"dates must be between {first} and {last}, inclusive (UTC window)", 422,
        )
