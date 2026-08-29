from datetime import date

import pytest
from pydantic import ValidationError

from climaprev.api.schemas.risk import RiskQueryParams
from climaprev.domain.units import TemperatureUnit


def test_location_text_defaults_to_celsius_and_same_day_period() -> None:
    params = RiskQueryParams(location_text="  Sao Paulo  ", start_date=date(2026, 8, 28))

    assert params.location_text == "Sao Paulo"
    assert params.end_date == date(2026, 8, 28)
    assert params.temperature_unit is TemperatureUnit.CELSIUS


def test_valid_coordinates_are_accepted() -> None:
    params = RiskQueryParams(
        latitude=-23.5505,
        longitude=-46.6333,
        start_date=date(2026, 8, 28),
    )

    assert params.location_text is None
    assert params.latitude == -23.5505
    assert params.longitude == -46.6333


def test_rejects_location_text_together_with_coordinates() -> None:
    with pytest.raises(ValidationError):
        RiskQueryParams(
            location_text="Sao Paulo",
            latitude=-23.5505,
            longitude=-46.6333,
            start_date=date(2026, 8, 28),
        )


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [(-23.5505, None), (None, -46.6333)],
)
def test_rejects_a_coordinate_without_its_pair(
    latitude: float | None, longitude: float | None
) -> None:
    with pytest.raises(ValidationError):
        RiskQueryParams(latitude=latitude, longitude=longitude, start_date=date(2026, 8, 28))


@pytest.mark.parametrize(
    ("latitude", "longitude"),
    [(90.1, 0.0), (-90.1, 0.0), (0.0, 180.1), (0.0, -180.1)],
)
def test_rejects_out_of_range_coordinates(latitude: float, longitude: float) -> None:
    with pytest.raises(ValidationError):
        RiskQueryParams(latitude=latitude, longitude=longitude, start_date=date(2026, 8, 28))


def test_rejects_an_empty_location_text_after_trimming() -> None:
    with pytest.raises(ValidationError):
        RiskQueryParams(location_text="   ", start_date=date(2026, 8, 28))


def test_rejects_an_end_date_before_start_date() -> None:
    with pytest.raises(ValidationError):
        RiskQueryParams(
            location_text="Sao Paulo",
            start_date=date(2026, 8, 28),
            end_date=date(2026, 8, 27),
        )


def test_rejects_an_inclusive_period_longer_than_seven_days() -> None:
    with pytest.raises(ValidationError):
        RiskQueryParams(
            location_text="Sao Paulo",
            start_date=date(2026, 8, 28),
            end_date=date(2026, 9, 4),
        )


def test_accepts_fahrenheit() -> None:
    params = RiskQueryParams(
        location_text="Sao Paulo",
        start_date=date(2026, 8, 28),
        temperature_unit=TemperatureUnit.FAHRENHEIT,
    )

    assert params.temperature_unit is TemperatureUnit.FAHRENHEIT


def test_rejects_an_invalid_temperature_unit() -> None:
    with pytest.raises(ValidationError) as error:
        RiskQueryParams(
            location_text="Sao Paulo",
            start_date=date(2026, 8, 28),
            temperature_unit="kelvin",
        )

    assert error.value.errors()[0]["loc"] == ("temperature_unit",)
