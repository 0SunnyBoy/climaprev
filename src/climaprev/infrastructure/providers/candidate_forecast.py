"""Deliver reviewed, prepared forecasts through the existing weather-provider port."""

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, cast

from climaprev.application.cache_codec import decode_forecast, encode_forecast
from climaprev.application.errors import WeatherDataInvalid, WeatherProviderUnavailable
from climaprev.domain.models import CanonicalLocation, DatePeriod, NormalizedForecast
from climaprev.tools.experimental_candidate import _sha, accepted_candidate, validate_candidate
from climaprev.tools.experimental_protocol import aware_timestamp
from climaprev.tools.historical_experiment import canonical_json, digest


def normalization_identity() -> dict[str, str]:
    root = Path(__file__).resolve().parents[2]
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
              for name in ("application/cache_codec.py", "infrastructure/providers/candidate_forecast.py")}
    return {"version": "prepared-normalized-v1", "sha256": digest(hashes)}


def prepare_forecast(
    candidate: dict[str, Any], forecast: NormalizedForecast, *, expires_at: datetime,
    source_hashes: dict[str, str],
) -> dict[str, Any]:
    """Package an offline result; writing this record does not approve its strategy."""
    value = validate_candidate(candidate)
    if (expires_at.utcoffset() is None or forecast.fetched_at.utcoffset() is None
            or expires_at <= forecast.fetched_at or set(source_hashes) != set(value["models"])
            or any(not _sha(checksum) for checksum in source_hashes.values())
            or value["normalization"] != normalization_identity()):
        raise ValueError("prepared forecast requires explicit chronology and source identities")
    record = {"schema": "climaprev-prepared-forecast-v1", "candidate_sha256": candidate["sha256"],
              "normalization": value["normalization"], "models": value["models"],
              "sources": source_hashes, "expires_at": expires_at.isoformat(),
              "forecast": encode_forecast(forecast)}
    return cast(dict[str, Any], json.loads(canonical_json({"prepared": record, "sha256": digest(record)})))


class PreparedCandidateForecast:
    def __init__(self, bundle: dict[str, Any], *, now: Callable[[], datetime] = lambda: datetime.now(UTC)) -> None:
        self._now = now
        self._entries: dict[tuple[float, float, date, date], tuple[NormalizedForecast, datetime]] = {}
        try:
            self.candidate = accepted_candidate(bundle["protocol"], bundle["candidate"],
                                                bundle["evaluation"], bundle["decision"])
            if (bundle.get("schema") != "climaprev-accepted-bundle-v1"
                    or self.candidate["normalization"] != normalization_identity() or not bundle["forecasts"]):
                raise ValueError("bundle normalization or prepared identity is invalid")
            self.strategy_identity = "candidate:" + digest(bundle)
            provenance = []
            for envelope in bundle["forecasts"]:
                record = envelope["prepared"]
                if (record.get("schema") != "climaprev-prepared-forecast-v1"
                        or envelope["sha256"] != digest(record)
                        or record["candidate_sha256"] != bundle["candidate"]["sha256"]
                        or record["normalization"] != self.candidate["normalization"]
                        or record["models"] != self.candidate["models"]
                        or set(record["sources"]) != set(self.candidate["models"])
                        or any(not _sha(checksum) for checksum in record["sources"].values())):
                    raise ValueError("prepared identity differs")
                data = record["forecast"]
                location = CanonicalLocation(**data["location"])
                period = DatePeriod(date.fromisoformat(data["period"]["start"]),
                                    date.fromisoformat(data["period"]["end"]))
                forecast = decode_forecast(data, location, period)
                expiry = aware_timestamp(record["expires_at"])
                key = self._key(location, period)
                if (forecast is None or forecast.fetched_at > now() or forecast.fetched_at >= expiry
                        or key in self._entries):
                    raise ValueError("prepared identity has invalid data, timing or duplicate scope")
                self._entries[key] = (forecast, expiry)
                provenance.append({"artifact_sha256": envelope["sha256"], "sources": record["sources"],
                                   "models": record["models"], "expires_at": record["expires_at"]})
            self._provenance = canonical_json(provenance)
        except (ValueError, TypeError, KeyError) as error:
            raise WeatherDataInvalid("candidate identity or prepared forecast is invalid") from error

    @property
    def provenance(self) -> list[dict[str, Any]]:
        return cast(list[dict[str, Any]], json.loads(self._provenance))

    @staticmethod
    def _key(location: CanonicalLocation, period: DatePeriod) -> tuple[float, float, date, date]:
        return location.latitude, location.longitude, period.start, period.end

    def assert_current(self, location: CanonicalLocation, period: DatePeriod) -> None:
        entry = self._entries.get(self._key(location, period))
        if entry is None:
            raise WeatherProviderUnavailable("no approved prepared forecast for this request")
        if self._now() >= entry[1]:
            raise WeatherProviderUnavailable("prepared candidate forecast expired")

    async def forecast(self, location: CanonicalLocation, period: DatePeriod) -> NormalizedForecast:
        self.assert_current(location, period)
        return self._entries[self._key(location, period)][0]
