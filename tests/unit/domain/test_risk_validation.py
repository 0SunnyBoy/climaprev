from datetime import UTC, date, datetime

from climaprev.domain.models import CanonicalLocation, DailyForecast, DatePeriod, NormalizedForecast
from climaprev.domain.risk_policy import RiskPolicy
from climaprev.domain.risk_validation import HistoricalRiskCase, validate_policy


def forecast_with_wind(gust: float) -> NormalizedForecast:
    return NormalizedForecast(
        location=CanonicalLocation(
            name="Sao Paulo",
            latitude=-23.5505,
            longitude=-46.6333,
            timezone="America/Sao_Paulo",
            source="test",
        ),
        period=DatePeriod(start=date(2026, 8, 28), end=date(2026, 8, 28)),
        days=(DailyForecast(
            date=date(2026, 8, 28),
            temperature_min_c=18.0,
            temperature_max_c=28.0,
            temperature_mean_c=23.0,
            humidity_mean_pct=70.0,
            precipitation_sum_mm=0.0,
            precipitation_probability_max_pct=0.0,
            precipitation_max_hourly_mm=0.0,
            wind_max_kmh=20.0,
            wind_gust_max_kmh=gust,
            weather_code=0,
        ),),
        provider="test",
        fetched_at=datetime(2026, 8, 28, tzinfo=UTC),
        is_stale=False,
        missing_fields=(),
    )


def test_reports_accuracy_and_directional_errors_for_reviewed_cases() -> None:
    report = validate_policy(
        (
            HistoricalRiskCase(forecast_with_wind(20.0), "low"),
            HistoricalRiskCase(forecast_with_wind(40.0), "moderate"),
            HistoricalRiskCase(forecast_with_wind(61.0), "moderate"),
        ),
        RiskPolicy(),
    )

    assert report.cases == 3
    assert report.correct == 2
    assert report.accuracy == 2 / 3
    assert report.false_positives == 1
    assert report.false_negatives == 0
