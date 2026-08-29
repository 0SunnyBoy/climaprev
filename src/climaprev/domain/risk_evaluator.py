from dataclasses import dataclass
from typing import Literal

from climaprev.domain.models import DailyForecast, NormalizedForecast, RiskAssessment, RiskCondition
from climaprev.domain.risk_policy import RiskPolicy

Severity = Literal["moderate", "high"]


@dataclass(frozen=True, slots=True)
class _Candidate:
    type: str
    severity: Severity
    value: float
    unit: str
    reason: str


class RiskEvaluator:
    def evaluate(self, forecast: NormalizedForecast, policy: RiskPolicy) -> RiskAssessment:
        selected: dict[str, _Candidate] = {}

        for day in forecast.days:
            rain = _rain_candidate(day, policy)
            if rain is not None:
                _select(selected, rain)
                _select(
                    selected,
                    _Candidate(
                        type="flooding_risk_proxy",
                        severity=rain.severity,
                        value=rain.value,
                        unit=rain.unit,
                        reason=(
                            "Forecast precipitation indicates a flooding risk proxy; "
                            "this is not a local hydrological assessment or an official alert."
                        ),
                    ),
                )

            wind = _wind_candidate(day, policy)
            if wind is not None:
                _select(selected, wind)

            temperature = _temperature_candidate(day, policy)
            if temperature is not None:
                _select(selected, temperature)

        conditions = tuple(
            RiskCondition(
                type=candidate.type,
                severity=candidate.severity,
                value=candidate.value,
                unit=candidate.unit,
                reason=candidate.reason,
            )
            for candidate in sorted(selected.values(), key=lambda candidate: candidate.type)
        )
        level = _assessment_level(conditions)
        return RiskAssessment(
            level=level,
            method="forecast_heuristic",
            policy_version=policy.policy_version,
            conditions=conditions,
        )


def _rain_candidate(day: DailyForecast, policy: RiskPolicy) -> _Candidate | None:
    candidates: list[_Candidate] = []
    hourly_severity = _at_least_severity(
        day.precipitation_max_hourly_mm,
        policy.hourly_rain_moderate_mm,
        policy.hourly_rain_high_mm,
    )
    if hourly_severity is not None and day.precipitation_max_hourly_mm is not None:
        candidates.append(
            _Candidate(
                type="heavy_rain_proxy",
                severity=hourly_severity,
                value=day.precipitation_max_hourly_mm,
                unit="mm/h",
                reason="Forecast hourly precipitation reached a heavy rain proxy, not an official alert.",
            )
        )

    daily_severity = _at_least_severity(
        day.precipitation_sum_mm,
        policy.daily_rain_moderate_mm,
        policy.daily_rain_high_mm,
    )
    if daily_severity is not None and day.precipitation_sum_mm is not None:
        candidates.append(
            _Candidate(
                type="heavy_rain_proxy",
                severity=daily_severity,
                value=day.precipitation_sum_mm,
                unit="mm/day",
                reason="Forecast daily precipitation reached a heavy rain proxy, not an official alert.",
            )
        )
    return _best(candidates)


def _wind_candidate(day: DailyForecast, policy: RiskPolicy) -> _Candidate | None:
    severity = _at_least_severity(
        day.wind_gust_max_kmh,
        policy.wind_gust_moderate_kmh,
        policy.wind_gust_high_kmh,
    )
    if severity is None or day.wind_gust_max_kmh is None:
        return None
    return _Candidate(
        type="strong_wind_proxy",
        severity=severity,
        value=day.wind_gust_max_kmh,
        unit="km/h",
        reason="Forecast wind gust reached a strong wind proxy, not an official alert.",
    )


def _temperature_candidate(day: DailyForecast, policy: RiskPolicy) -> _Candidate | None:
    candidates: list[_Candidate] = []
    maximum_severity = _at_least_severity(
        day.temperature_max_c,
        policy.temperature_max_moderate_c,
        policy.temperature_max_high_c,
    )
    if maximum_severity is not None and day.temperature_max_c is not None:
        candidates.append(
            _Candidate(
                type="temperature_extreme_proxy",
                severity=maximum_severity,
                value=day.temperature_max_c,
                unit="celsius",
                reason=(
                    "Forecast maximum temperature reached an absolute temperature extreme proxy, "
                    "not a heatwave or official alert."
                ),
            )
        )

    minimum_severity = _at_most_severity(
        day.temperature_min_c,
        policy.temperature_min_moderate_c,
        policy.temperature_min_high_c,
    )
    if minimum_severity is not None and day.temperature_min_c is not None:
        candidates.append(
            _Candidate(
                type="temperature_extreme_proxy",
                severity=minimum_severity,
                value=day.temperature_min_c,
                unit="celsius",
                reason=(
                    "Forecast minimum temperature reached an absolute temperature extreme proxy, "
                    "not a heatwave or official alert."
                ),
            )
        )
    return _best(candidates)


def _at_least_severity(value: float | None, moderate: float, high: float) -> Severity | None:
    if value is None:
        return None
    if value >= high:
        return "high"
    if value >= moderate:
        return "moderate"
    return None


def _at_most_severity(value: float | None, moderate: float, high: float) -> Severity | None:
    if value is None:
        return None
    if value <= high:
        return "high"
    if value <= moderate:
        return "moderate"
    return None


def _select(selected: dict[str, _Candidate], candidate: _Candidate) -> None:
    existing = selected.get(candidate.type)
    if existing is None or _candidate_key(candidate) > _candidate_key(existing):
        selected[candidate.type] = candidate


def _best(candidates: list[_Candidate]) -> _Candidate | None:
    if not candidates:
        return None
    return max(candidates, key=_candidate_key)


def _candidate_key(candidate: _Candidate) -> tuple[int, float, str]:
    severity_rank = 2 if candidate.severity == "high" else 1
    return severity_rank, abs(candidate.value), candidate.unit


def _assessment_level(
    conditions: tuple[RiskCondition, ...],
) -> Literal["low", "moderate", "high"]:
    if any(condition.severity == "high" for condition in conditions):
        return "high"
    if conditions:
        return "moderate"
    return "low"
