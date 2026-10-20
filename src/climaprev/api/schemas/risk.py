from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

from climaprev.domain.units import TemperatureUnit


class RiskQueryParams(BaseModel):
    location_text: str | None = Field(default=None, min_length=1, max_length=200)
    latitude: float | None = None
    longitude: float | None = None
    start_date: date = Field(description="Date within today through UTC today + 6 days, inclusive.")
    end_date: date | None = Field(default=None, description=(
        "Defaults to start_date. Same seven-date UTC eligibility window; at most seven consecutive dates."
    ))
    temperature_unit: TemperatureUnit = TemperatureUnit.CELSIUS

    @field_validator("location_text")
    @classmethod
    def trim_location_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()

    @model_validator(mode="after")
    def validate_query(self) -> "RiskQueryParams":
        has_location_text = self.location_text is not None
        has_latitude = self.latitude is not None
        has_longitude = self.longitude is not None

        if self.location_text == "":
            raise ValueError("location_text must not be empty")
        if has_location_text and (has_latitude or has_longitude):
            raise ValueError("location_text and coordinates cannot be used together")
        if has_latitude != has_longitude:
            raise ValueError("latitude and longitude must be provided together")
        if not has_location_text and not has_latitude:
            raise ValueError("location_text or coordinates must be provided")
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if self.longitude is not None and not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")

        if self.end_date is None:
            self.end_date = self.start_date
        elif self.end_date < self.start_date:
            raise ValueError("end_date must not be before start_date")

        if (self.end_date - self.start_date).days + 1 > 7:
            raise ValueError("date period must not exceed seven days")

        return self
