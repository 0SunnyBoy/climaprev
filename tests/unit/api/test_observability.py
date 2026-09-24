from __future__ import annotations

from climaprev.api.observability import RequestMetrics
from climaprev.domain.models import RiskAssessment


def test_records_the_clima_11_metric_contract_without_request_payloads() -> None:
    metrics = RequestMetrics()
    metrics.record_request(
        method="GET",
        route="/api/v1/risk",
        status_code=200,
        duration_seconds=0.05,
        cache=None,
        error_code=None,
        provider=None,
    )
    metrics.record_provider_request(provider="open-meteo", duration_seconds=0.12, outcome="error")
    metrics.record_cache_status("stale")
    metrics.record_rate_limit_rejection()
    metrics.record_risk_evaluation(
        RiskAssessment(level="high", method="forecast_heuristic", policy_version="reference-v1", conditions=())
    )
    metrics.record_missing_fields(("daily.weather_code",))
    metrics.record_dependency_circuit_state("weather_provider", "closed")

    snapshot = metrics.snapshot()

    assert snapshot["http_requests_total"]["GET|/api/v1/risk|200"] == 1
    assert snapshot["http_request_duration_seconds"]["count"] == 1
    assert snapshot["request_latency_ms"] == {
        "sample_count": 1,
        "p50": 50.0,
        "p95": 50.0,
        "p99": 50.0,
    }
    assert snapshot["weather_provider_requests_total"]["open-meteo|error"] == 1
    assert snapshot["weather_provider_latency_ms"]["open-meteo"] == {
        "sample_count": 1,
        "p50": 120.0,
        "p95": 120.0,
        "p99": 120.0,
    }
    assert snapshot["weather_provider_request_duration_seconds"]["count"] == 1
    assert snapshot["cache_stale_total"] == 1
    assert snapshot["rate_limit_rejections_total"] == 1
    assert snapshot["risk_evaluations_total"]["high|reference-v1"] == 1
    assert snapshot["weather_missing_fields_total"]["daily.weather_code"] == 1
    assert snapshot["http_status_429_total"] == 0
    assert snapshot["http_status_502_total"] == 0
    assert snapshot["http_status_503_total"] == 0
    assert snapshot["dependency_circuit_state"]["weather_provider"] == "closed"


def test_latency_samples_are_bounded_without_losing_request_counts() -> None:
    metrics = RequestMetrics()

    for _ in range(2_100):
        metrics.record_request(
            status_code=200,
            duration_seconds=0.1,
            cache=None,
            error_code=None,
        )

    snapshot = metrics.snapshot()

    assert snapshot["requests_total"] == 2_100
    assert snapshot["request_latency_ms"]["sample_count"] == 2_048
    assert snapshot["request_latency_ms"]["p50"] == 100.0
