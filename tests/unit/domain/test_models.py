from datetime import date

import pytest

from climaprev.domain.models import CanonicalLocation, DatePeriod


def test_canonical_location_accepts_valid_coordinates_and_iana_timezone() -> None:
    location = CanonicalLocation("Sao Paulo", -23.55, -46.63, "America/Sao_Paulo", "test")

    assert location.latitude == -23.55


@pytest.mark.parametrize(
    ("latitude", "longitude", "timezone"),
    [
        (91.0, 0.0, "UTC"),
        (0.0, 181.0, "UTC"),
        (0.0, 0.0, "Not/AZone"),
    ],
)
def test_canonical_location_rejects_invalid_coordinates_or_timezone(
    latitude: float,
    longitude: float,
    timezone: str,
) -> None:
    with pytest.raises(ValueError):
        CanonicalLocation("Invalid", latitude, longitude, timezone, "test")


def test_date_period_still_defends_against_reversed_ranges() -> None:
    with pytest.raises(ValueError):
        DatePeriod(start=date(2026, 1, 2), end=date(2026, 1, 1))
