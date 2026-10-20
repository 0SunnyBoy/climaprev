"""Count diagnostic event support on quality-checked station days; never fit labels."""

from collections import Counter
from math import isfinite
from typing import Any

from climaprev.domain.risk_policy import RiskPolicy, policy_fingerprint


def summarize_support(observations: dict[str, Any],
                      dates_by_variable: dict[str, list[str]]) -> dict[str, Any]:
    """Use frozen v1 boundaries only; counts are not approval or independent impacts."""
    policy = RiskPolicy()
    days = {day['date']: day for day in observations['days']}
    if len(days) != len(observations['days']):
        raise ValueError('duplicate observation dates')
    definitions = (
        ('hourly_rain', 'rain_mm', 'max_hourly_mm', policy.hourly_rain_moderate_mm,
         policy.hourly_rain_high_mm, False),
        ('daily_rain', 'rain_mm', 'value', policy.daily_rain_moderate_mm,
         policy.daily_rain_high_mm, False),
        ('gust', 'gust_kmh', 'value', policy.wind_gust_moderate_kmh,
         policy.wind_gust_high_kmh, False),
        ('heat', 'temperature_max_c', 'value', policy.temperature_max_moderate_c,
         policy.temperature_max_high_c, False),
        ('cold', 'temperature_min_c', 'value', policy.temperature_min_moderate_c,
         policy.temperature_min_high_c, True),
    )
    events = {}
    for event, variable, value_key, moderate, high, decreasing in definitions:
        dates = dates_by_variable[variable]
        if len(dates) != len(set(dates)):
            raise ValueError('duplicate eligible dates')
        counts: Counter[str] = Counter(low=0, moderate=0, high=0)
        high_dates = []
        for day in dates:
            if day not in days:
                raise ValueError('eligible date absent from observations')
            field = days[day]['fields'][variable]
            value = field.get(value_key)
            if (field.get('eligible') is not True or isinstance(value, bool)
                    or not isinstance(value, int | float) or not isfinite(value)):
                raise ValueError('eligible date has incomplete or invalid observation')
            is_high = value <= high if decreasing else value >= high
            is_moderate = value <= moderate if decreasing else value >= moderate
            level = 'high' if is_high else 'moderate' if is_moderate else 'low'
            counts[level] += 1
            if is_high:
                high_dates.append(day)
        events[event] = {'eligible_days': len(dates), 'counts': dict(counts),
                         'high_dates': sorted(high_dates),
                         'high_support_present': counts['high'] > 0,
                         'sample_sufficiency_approved': False}
    return {'schema': 'climaprev-observation-support-v1',
            'policy_version': policy.policy_version, 'policy_sha256': policy_fingerprint(policy),
            'events': events, 'scientific_approval': False, 'calibration_ready': False,
            'limitation': 'Diagnostic threshold support, not frozen scientific targets, '
                          'independent events or observed disaster impacts.'}
