from climaprev.domain.units import TemperatureUnit, convert_temperature


def test_convert_temperature_converts_freezing_point_to_fahrenheit() -> None:
    assert convert_temperature(0.0, TemperatureUnit.FAHRENHEIT) == 32.0


def test_convert_temperature_converts_boiling_point_to_fahrenheit() -> None:
    assert convert_temperature(100.0, TemperatureUnit.FAHRENHEIT) == 212.0


def test_convert_temperature_preserves_none() -> None:
    assert convert_temperature(None, TemperatureUnit.FAHRENHEIT) is None


def test_convert_temperature_preserves_celsius_value() -> None:
    assert convert_temperature(23.5, TemperatureUnit.CELSIUS) == 23.5
