from climaprev.domain.risk_policy import RiskPolicy


def test_reference_policy_exposes_configurable_thresholds_and_fixed_version() -> None:
    policy = RiskPolicy(
        hourly_rain_moderate_mm=21.0,
        daily_rain_high_mm=51.0,
        wind_gust_high_kmh=62.0,
        temperature_min_high_c=-1.0,
    )

    assert policy.hourly_rain_moderate_mm == 21.0
    assert policy.daily_rain_high_mm == 51.0
    assert policy.wind_gust_high_kmh == 62.0
    assert policy.temperature_min_high_c == -1.0
    assert policy.policy_version == "reference-v1"


def test_reference_policy_uses_the_v1_default_thresholds() -> None:
    policy = RiskPolicy()

    assert policy.hourly_rain_moderate_mm == 20.0
    assert policy.hourly_rain_high_mm == 30.0
    assert policy.daily_rain_moderate_mm == 30.0
    assert policy.daily_rain_high_mm == 50.0
    assert policy.wind_gust_moderate_kmh == 40.0
    assert policy.wind_gust_high_kmh == 61.0
    assert policy.temperature_max_moderate_c == 35.0
    assert policy.temperature_max_high_c == 40.0
    assert policy.temperature_min_moderate_c == 5.0
    assert policy.temperature_min_high_c == 0.0
