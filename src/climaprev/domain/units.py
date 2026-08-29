from enum import StrEnum


class TemperatureUnit(StrEnum):
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"


def convert_temperature(
    value_celsius: float | None,
    target: TemperatureUnit,
) -> float | None:
    if value_celsius is None:
        return None
    if target is TemperatureUnit.CELSIUS:
        return value_celsius
    return value_celsius * 9.0 / 5.0 + 32.0
