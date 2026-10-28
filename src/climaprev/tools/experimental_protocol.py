"""Versioned local experiment contracts; validation never reads outcomes or uses HTTP."""

import json
from datetime import UTC, date, datetime
from math import isfinite
from typing import Any, cast
from zoneinfo import ZoneInfo

from climaprev.tools.experimental_collection import MODELS
from climaprev.tools.historical_experiment import canonical_json, digest

SCHEMA = "climaprev-experiment-protocol-v1"
_FIELDS = {"schema", "id", "code_version", "stations", "variables", "models", "slots",
           "horizons", "slot_window_minutes", "provider_daily_call_limit", "splits", "criteria"}


def aware_timestamp(value: str) -> datetime:
    stamp = datetime.fromisoformat(value)
    if stamp.utcoffset() is None:
        raise ValueError("experiment timestamp requires a UTC offset")
    return stamp.astimezone(UTC)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _positive(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def validate_protocol(envelope: dict[str, Any]) -> dict[str, Any]:
    """Return an independent JSON value after checking structure and content identity."""
    if set(envelope) != {"protocol", "sha256"}:
        raise ValueError("protocol envelope requires protocol and sha256")
    protocol = envelope["protocol"]
    if not isinstance(protocol, dict) or set(protocol) != _FIELDS:
        raise ValueError("protocol fields are incomplete or unknown")
    if protocol["schema"] != SCHEMA:
        raise ValueError("unsupported protocol schema")
    if envelope["sha256"] != digest(protocol):
        raise ValueError("protocol hash differs")
    if not all(_text(protocol[key]) for key in ("id", "code_version")):
        raise ValueError("protocol identity and code version are required")
    for key in ("stations", "variables", "models", "slots", "horizons"):
        if not isinstance(protocol[key], list) or not protocol[key]:
            raise ValueError(f"protocol requires nonempty {key}")
    for key in ("slot_window_minutes", "provider_daily_call_limit"):
        if not _positive(protocol[key]):
            raise ValueError(f"protocol {key} must be a positive integer")
    if any(not _positive(lead) or lead > 7 for lead in protocol["horizons"]):
        raise ValueError("protocol horizons must be integers from one to seven")
    for key in ("models", "slots", "horizons"):
        if len({canonical_json(item) for item in protocol[key]}) != len(protocol[key]):
            raise ValueError(f"duplicate protocol {key}")
    if any(model not in {*MODELS, "operational-baseline"} for model in protocol["models"]):
        raise ValueError("unsupported protocol model")
    for slot in protocol["slots"]:
        if not _text(slot):
            raise ValueError("protocol slots require timestamps")
        aware_timestamp(slot)
    codes = set()
    for station in protocol["stations"]:
        if not isinstance(station, dict) or set(station) != {
            "code", "name", "latitude", "longitude", "timezone",
        }:
            raise ValueError("invalid protocol station fields")
        if not all(_text(station[key]) for key in ("code", "name", "timezone")):
            raise ValueError("protocol station identity is missing")
        for field, bound in (("latitude", 90), ("longitude", 180)):
            value = station[field]
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not isfinite(value) or abs(value) > bound):
                raise ValueError("invalid protocol coordinates")
        ZoneInfo(station["timezone"])
        if station["code"] in codes:
            raise ValueError("duplicate protocol station")
        codes.add(station["code"])
    variables = set()
    for variable in protocol["variables"]:
        if not isinstance(variable, dict) or set(variable) != {
            "name", "unit", "semantics", "aggregation",
        } or not all(_text(value) for value in variable.values()):
            raise ValueError("invalid protocol variable contract")
        if variable["aggregation"] not in {"sum", "min", "max", "mean", "instant"}:
            raise ValueError("unsupported protocol aggregation")
        if variable["name"] in variables:
            raise ValueError("duplicate protocol variable")
        variables.add(variable["name"])
    if not isinstance(protocol["splits"], dict) or not isinstance(protocol["criteria"], dict):
        raise TypeError("protocol splits and criteria must be objects")
    _partition_bounds(protocol)
    return cast(dict[str, Any], json.loads(canonical_json(protocol)))


def _partition_bounds(protocol: dict[str, Any]) -> dict[str, tuple[date, date]]:
    splits = protocol["splits"]
    if set(splits) != {"adjustment", "validation", "test"}:
        raise ValueError("protocol requires adjustment, validation and test partitions")
    previous: date | None = None
    result = {}
    for name in ("adjustment", "validation", "test"):
        bounds = splits[name]
        if not isinstance(bounds, dict) or set(bounds) != {"start", "end"}:
            raise ValueError("partition requires start and end")
        start, end = date.fromisoformat(bounds["start"]), date.fromisoformat(bounds["end"])
        if start > end or (previous is not None and start <= previous):
            raise ValueError("partitions must be chronological and disjoint")
        result[name] = (start, end)
        previous = end
    return result


def partition_for(envelope: dict[str, Any], target: date) -> str | None:
    protocol = validate_protocol(envelope)
    return next((name for name, (start, end) in _partition_bounds(protocol).items()
                 if start <= target <= end), None)
