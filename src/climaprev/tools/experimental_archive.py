"""Archive already collected experimental forecasts; no HTTP, fitting or promotion."""

import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit

from climaprev.domain.models import CanonicalLocation
from climaprev.tools.historical_experiment import canonical_json, digest, read_json

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


def _file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save_evidence(
    path: Path, *, protocol_sha256: str, parents: dict[str, Path], code_version: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Bind a result to exact local inputs; never overwrite divergent evidence."""
    if not code_version.strip():
        raise ValueError("evidence code version is required")
    if re.fullmatch(r"[0-9a-f]{64}", protocol_sha256) is None:
        raise ValueError("evidence requires a protocol SHA256")
    data = {"schema": "climaprev-experiment-evidence-v1",
            "protocol_sha256": protocol_sha256, "code_version": code_version,
            "inputs": {name: {"path": str(parent.resolve()), "sha256": _file_sha256(parent)}
                       for name, parent in sorted(parents.items())}, "payload": payload}
    encoded = canonical_json({"sha256": digest(data), "evidence": data}).encode()
    if len(encoded) > 4 * 1024 * 1024:
        raise ValueError("experimental evidence exceeds 4 MiB")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb") as stream:
            stream.write(encoded)
    except FileExistsError:
        if path.read_bytes() != encoded:
            raise ValueError("refusing to overwrite divergent evidence") from None
    return load_evidence(path)


def load_evidence(path: Path) -> dict[str, Any]:
    envelope = read_json(path)
    data = envelope.get("evidence")
    if (not isinstance(data, dict) or data.get("schema") != "climaprev-experiment-evidence-v1"
            or envelope.get("sha256") != digest(data)):
        raise ValueError("invalid evidence schema or hash")
    for parent in data["inputs"].values():
        if _file_sha256(Path(parent["path"])) != parent["sha256"]:
            raise ValueError("evidence parent differs from its frozen identity")
    return data


def load_forecast_capture(
    path: Path, *, model: str | None = None, location: CanonicalLocation | None = None,
) -> dict[str, Any]:
    """Read a content-addressed capture and validate its declared provenance."""
    capture = read_json(path)
    if (capture.get("schema") != "climaprev-experimental-archive-v1"
            or capture.get("payload_sha256") != digest(capture["payload"])
            or path.stem != digest(capture)):
        raise ValueError("capture identity differs")
    metadata = capture["metadata"]
    if not isinstance(metadata, dict):
        raise TypeError("capture metadata must be an object")
    point = CanonicalLocation(**metadata["location"])
    ForecastCapture(
        metadata["provider"], metadata["model"], metadata["endpoint"], point,
        datetime.fromisoformat(metadata["collected_at"]),
        datetime.fromisoformat(metadata["valid_start"]), datetime.fromisoformat(metadata["valid_end"]),
        datetime.fromisoformat(metadata["run_at"]) if metadata["run_at"] else None,
        metadata["selection_mode"],
    )
    expected = {"met-norway": "ecmwf-ifs-global-unspecified",
                "operational-baseline": "unknown"}.get(model, model) if model else None
    if expected is not None and metadata["model"] != expected:
        raise ValueError("capture model differs from the declared arm")
    if location is not None and any(getattr(point, key) != getattr(location, key)
                                    for key in ("latitude", "longitude", "timezone")):
        raise ValueError("capture point differs from station")
    return capture
