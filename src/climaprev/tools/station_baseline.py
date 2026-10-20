"""Diagnostic v1 classification against station measurements; no fitting or promotion."""

from collections.abc import Sequence
from dataclasses import asdict
from math import isfinite
from typing import Any

from climaprev.domain.risk_policy import RiskPolicy, policy_fingerprint
from climaprev.domain.verification import Level, classify_pairs


def event_level(event: str, value: float) -> Level:
    policy = RiskPolicy()
    thresholds = {
        'hourly_rain': (policy.hourly_rain_moderate_mm, policy.hourly_rain_high_mm),
        'daily_rain': (policy.daily_rain_moderate_mm, policy.daily_rain_high_mm),
        'gust': (policy.wind_gust_moderate_kmh, policy.wind_gust_high_kmh),
        'heat': (policy.temperature_max_moderate_c, policy.temperature_max_high_c),
        'cold': (policy.temperature_min_moderate_c, policy.temperature_min_high_c),
    }
    if event not in thresholds:
        raise ValueError('unsupported baseline event')
    if isinstance(value, bool) or not isfinite(value):
        raise ValueError('baseline values must be finite numbers')
    moderate, high = thresholds[event]
    if (value <= high if event == 'cold' else value >= high):
        return 'high'
    if (value <= moderate if event == 'cold' else value >= moderate):
        return 'moderate'
    return 'low'


def baseline_event(event: str, cases: Sequence[dict[str, Any]]) -> dict[str, Any]:
    seen = set()
    pairs: dict[str, list[tuple[Level, Level]]] = {'forecast': [], 'observed': []}
    for row in cases:
        identity = (row['location'], row['date'])
        if identity in seen:
            raise ValueError('duplicate location/date in one horizon')
        seen.add(identity)
        target = event_level(event, row['station'])
        for source, values in pairs.items():
            values.append((target, event_level(event, row[source])))
    return {'event': event, 'cases': len(cases),
            'policy_version': 'reference-v1', 'policy_sha256': policy_fingerprint(RiskPolicy()),
            'scores': {source: asdict(classify_pairs(values)) for source, values in pairs.items()},
            'scientific_approval': False, 'calibration_ready': False,
            'limitation': 'forecast is GFS, observed is ERA5 diagnostic control; '
                          'station thresholds describe weather, not disaster impacts. '
                          'Sampling semantics differ for gust and temperature. '
                          'Event-only thresholds on experimental aggregates, not an '
                          'end-to-end replay of API normalization or risk-overview priority.'}
