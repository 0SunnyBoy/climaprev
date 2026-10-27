"""Archive already collected experimental forecasts; no HTTP, fitting or promotion."""

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.historical_experiment import canonical_json, digest

_HOSTS = {"open-meteo": {"api.open-meteo.com", "single-runs-api.open-meteo.com"},
          "met-norway": {"api.met.no"}}


@dataclass(frozen=True, slots=True)
class ForecastCapture:
    provider: str
    model: str
    endpoint: str
    location: CanonicalLocation
    collected_at: datetime
    valid_start: datetime
    valid_end: datetime
    run_at: datetime | None = None
    selection_mode: Literal["explicit", "automatic"] = "explicit"

    def __post_init__(self) -> None:
        url = urlsplit(self.endpoint)
        if (self.provider not in _HOSTS or url.scheme != "https"
                or url.hostname not in _HOSTS[self.provider] or url.port not in {None, 443}
                or url.username is not None or url.password is not None
                or url.query or url.fragment):
            raise ValueError("experimental endpoint must be an allowed HTTPS URL without query")
        if not self.model.strip() or self.model.strip().lower() in {"auto", "best_match"}:
            raise ValueError("an explicit model identity is required")
        if self.selection_mode not in {"explicit", "automatic"}:
            raise ValueError("unknown selection mode")
        if self.selection_mode == "automatic" and (
            self.provider != "open-meteo" or self.model != "unknown"
            or self.run_at is not None or url.hostname != "api.open-meteo.com"
        ):
            raise ValueError("automatic selection must preserve unknown model and run")
        if self.selection_mode == "explicit" and self.model == "unknown":
            raise ValueError("unknown model requires automatic selection")
        for value in (self.collected_at, self.valid_start, self.valid_end, self.run_at):
            if value is not None and value.utcoffset() is None:
                raise ValueError("capture timestamps must have a UTC offset")
        if self.valid_start.astimezone(UTC) >= self.valid_end.astimezone(UTC):
            raise ValueError("validity must be a nonempty half-open interval")
        if (self.run_at is not None
                and self.run_at.astimezone(UTC) > self.collected_at.astimezone(UTC)):
            raise ValueError("model run cannot be later than collection")


def archive_forecast(
    directory: Path, capture: ForecastCapture, payload: dict[str, Any],
) -> Path:
    """Preserve raw JSON and provenance under an immutable content-addressed name.

    Chronology checks are necessary, not scientific approval or verification
    that the provider really supplied the declared model/run timestamps.
    """
    def stamp(value: datetime) -> str:
        return value.astimezone(UTC).isoformat()

    timing_issues = []
    if capture.run_at is None:
        timing_issues.append("model_run_unknown")
    elif capture.run_at.astimezone(UTC) >= capture.valid_start.astimezone(UTC):
        timing_issues.append("model_run_not_before_target")
    if capture.collected_at.astimezone(UTC) >= capture.valid_start.astimezone(UTC):
        timing_issues.append("collected_not_before_target")
    metadata = {
        "provider": capture.provider, "model": capture.model, "endpoint": capture.endpoint,
        "selection_mode": capture.selection_mode,
        "location": asdict(capture.location), "collected_at": stamp(capture.collected_at),
        "valid_start": stamp(capture.valid_start), "valid_end": stamp(capture.valid_end),
        "interval_convention": "[valid_start,valid_end)",
        "run_at": stamp(capture.run_at) if capture.run_at else None,
        "run_lead_hours": ((capture.valid_start.astimezone(UTC)
                            - capture.run_at.astimezone(UTC)).total_seconds() / 3600
                           if capture.run_at else None),
        "collection_lead_hours": ((capture.valid_start.astimezone(UTC)
                                   - capture.collected_at.astimezone(UTC)).total_seconds() / 3600),
        "timing_issues": timing_issues,
    }
    envelope = {
        "schema": "climaprev-experimental-archive-v1", "metadata": metadata,
        "payload_sha256": digest(payload), "payload": payload,
        "evaluation_status": "not_evaluated", "scientific_approval": False,
    }
    encoded = canonical_json(envelope).encode("utf-8")
    if len(encoded) > 4 * 1024 * 1024:
        raise ValueError("experimental archive exceeds 4 MiB")
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{digest(envelope)}.json"
    try:
        with path.open("xb") as stream:
            stream.write(encoded)
    except FileExistsError:
        if path.read_bytes() != encoded:
            raise ValueError("existing archive content differs from its identity") from None
    return path
