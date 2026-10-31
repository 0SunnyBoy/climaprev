import pytest

from climaprev.tools.error_catalog import catalog_pair, detection


@pytest.mark.parametrize("actual,predicted,expected", [
    ("high", "high", "hit"), ("high", "moderate", "miss"),
    ("low", "high", "false_alarm"), ("moderate", "low", "correct_negative"),
])
def test_high_detection_definition(actual, predicted, expected):
    assert detection(actual, predicted) == expected


def test_catalog_preserves_values_both_sources_and_non_high_denominator():
    left = [{"date": "01", "station": 51, "forecast": 49, "observed": 60},
            {"date": "02", "station": 0, "forecast": 0, "observed": 0}]
    right = [{"date": "01", "station": 51, "forecast": 52, "observed": 40}, left[1]]
    rows = catalog_pair("daily_rain", left, right, {"01", "02"})
    assert len(rows) == 2
    assert rows[0]["arms"]["municipal-control"]["forecast"]["high_detection"] == "miss"
    assert rows[0]["arms"]["station"]["forecast"]["high_detection"] == "hit"
    assert rows[0]["arms"]["station"]["forecast"]["value"] == 52
    assert rows[0]["arms"]["municipal-control"]["observed"]["high_detection"] == "hit"
    assert rows[0]["high_relevant"]
    assert not rows[1]["high_relevant"]


def test_cold_uses_reversed_thresholds_and_missing_date_is_excluded():
    row = {"date": "01", "station": -1, "forecast": 1, "observed": -2}
    result = catalog_pair("cold", [row], [row], {"01", "02"})
    assert len(result) == 1
    assert result[0]["station_level"] == "high"
    assert result[0]["arms"]["station"]["forecast"]["high_detection"] == "miss"
