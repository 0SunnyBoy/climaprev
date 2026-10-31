"""Trace high-event detections to measured values, without changing thresholds."""

from typing import Any

from climaprev.domain.risk_policy import RiskPolicy
from climaprev.tools.spatial_comparison import paired_cases
from climaprev.tools.station_baseline import event_level


def detection(actual: str, predicted: str) -> str:
    if actual == "high":
        return "hit" if predicted == "high" else "miss"
    return "false_alarm" if predicted == "high" else "correct_negative"


def catalog_pair(
    event: str, control: list[dict[str, Any]], station: list[dict[str, Any]], eligible: set[str],
) -> list[dict[str, Any]]:
    """Retain every paired case so counts, omissions and selected errors are auditable."""
    left, right = paired_cases(control, station, eligible)
    policy = RiskPolicy()
    thresholds = {
        "daily_rain": (policy.daily_rain_moderate_mm, policy.daily_rain_high_mm),
        "hourly_rain": (policy.hourly_rain_moderate_mm, policy.hourly_rain_high_mm),
        "gust": (policy.wind_gust_moderate_kmh, policy.wind_gust_high_kmh),
        "heat": (policy.temperature_max_moderate_c, policy.temperature_max_high_c),
        "cold": (policy.temperature_min_moderate_c, policy.temperature_min_high_c),
    }
    moderate, high = thresholds[event]
    result = []
    for municipal, at_station in zip(left, right, strict=True):
        actual = event_level(event, municipal["station"])
        arms = {}
        for arm, row in (("municipal-control", municipal), ("station", at_station)):
            arms[arm] = {
                source: {"value": row[source], "level": event_level(event, row[source]),
                         "error": row[source] - row["station"],
                         "margin_to_moderate": (moderate - row[source] if event == "cold"
                                                else row[source] - moderate),
                         "margin_to_high": (high - row[source] if event == "cold"
                                            else row[source] - high),
                         "at_least_moderate_detection": detection(
                             "high" if actual != "low" else "low",
                             "high" if event_level(event, row[source]) != "low" else "low"),
                         "high_detection": detection(actual, event_level(event, row[source]))}
                for source in ("forecast", "observed")}
        result.append({
            "date": municipal["date"], "station_value": municipal["station"],
            "station_level": actual, "arms": arms,
            "thresholds": {"moderate": moderate, "high": high,
                           "margin_sign": "nonnegative means meets or exceeds severity threshold"},
            "high_relevant": actual == "high" or any(
                values["level"] == "high" for arm in arms.values() for values in arm.values()),
            "cause": "not_established_by_descriptive_comparison",
        })
    return result
