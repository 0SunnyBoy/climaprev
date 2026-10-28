"""Exploratory measurement-contract checks, without pairing, scoring or approval."""

from dataclasses import dataclass
from datetime import UTC, timedelta
from math import isfinite

from climaprev.tools.experimental_normalization import Measurement


@dataclass(frozen=True, slots=True)
class EquivalenceCheck:
    target: str
    compatible_measurements: bool
    exclusions: tuple[str, ...]
    scientific_approval: bool = False
    promotion_allowed: bool = False


def _rain_duration(semantics: str) -> timedelta | None:
    hours = {
        "previous_hour_sum": 1, "observed_previous_hour_sum": 1,
        "next_1_hours_sum": 1, "next_6_hours_sum": 6, "next_12_hours_sum": 12,
    }.get(semantics)
    return timedelta(hours=hours) if hours else None


def check_equivalence(
    target: str, forecast: Measurement, observation: Measurement,
) -> EquivalenceCheck:
    """Check values, units, interval and declared semantics for one measurement pair.

    A compatible pair does not establish station/grid representativeness, source
    authenticity, model-run eligibility, instrument comparability or approval.
    Observed instantaneous fields are prospective contracts, not fields currently
    imported by the INMET adapter. No aggregation or missing-value filling occurs.
    """
    contracts = {
        "rain_accumulation": ("precipitation_mm", "mm", None, None),
        "gust_previous_hour_max": ("gust_kmh", "km/h", "previous_hour_max",
                                   "observed_previous_hour_max"),
        "temperature_previous_hour_max": ("temperature_c", "°C", "previous_hour_max",
                                          "observed_previous_hour_max"),
        "temperature_previous_hour_min": ("temperature_c", "°C", "previous_hour_min",
                                          "observed_previous_hour_min"),
        "temperature_instant": ("temperature_c", "°C", "instant", "observed_instant"),
        "humidity_instant": ("humidity_pct", "%", "instant", "observed_instant"),
    }
    if target not in contracts:
        raise ValueError("unsupported target; wind averaging needs a separate contract")
    variable, unit, forecast_semantics, observed_semantics = contracts[target]
    reasons = []
    for role, item, semantics in (("forecast", forecast, forecast_semantics),
                                  ("observation", observation, observed_semantics)):
        if item.variable != variable:
            reasons.append(f"{role}_variable")
        if item.unit != unit:
            reasons.append(f"{role}_unit")
        value = item.value
        if value is None:
            reasons.append(f"{role}_missing")
        elif (isinstance(value, bool) or not isinstance(value, (int, float))
              or not isfinite(value) or (variable != "temperature_c" and value < 0)
              or (variable == "humidity_pct" and value > 100)):
            reasons.append(f"{role}_invalid_value")
        if item.start.utcoffset() is None or (item.end and item.end.utcoffset() is None):
            reasons.append(f"{role}_naive_time")
            continue
        if target == "rain_accumulation":
            duration = _rain_duration(item.semantics)
            if (role == "observation" and item.semantics == "observed_interval_sum"
                    and item.end is not None):
                duration = item.end.astimezone(UTC) - item.start.astimezone(UTC)
                if duration <= timedelta(0):
                    duration = None
            elif role == "observation" and item.semantics != "observed_previous_hour_sum":
                duration = None
            if role == "forecast" and item.semantics.startswith("observed_"):
                duration = None
        elif semantics in {"instant", "observed_instant"}:
            duration = None
            if item.semantics != semantics or item.end is not None:
                reasons.append(f"{role}_semantics")
            continue
        else:
            duration = timedelta(hours=1) if item.semantics == semantics else None
        if duration is None:
            reasons.append(f"{role}_semantics")
        elif (item.end is None
              or item.end.astimezone(UTC) - item.start.astimezone(UTC) != duration):
            reasons.append(f"{role}_interval")
    if (forecast.start.utcoffset() is not None and observation.start.utcoffset() is not None
            and forecast.start.astimezone(UTC) != observation.start.astimezone(UTC)):
        reasons.append("different_start")
    if (forecast.end is None) != (observation.end is None):
        reasons.append("different_interval_kind")
    elif (forecast.end is not None and observation.end is not None
          and forecast.end.utcoffset() is not None and observation.end.utcoffset() is not None
          and forecast.end.astimezone(UTC) != observation.end.astimezone(UTC)):
        reasons.append("different_end")
    return EquivalenceCheck(target, not reasons, tuple(reasons))
