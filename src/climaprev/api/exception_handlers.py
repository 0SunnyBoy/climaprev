"""Translate application failures into the public HTTP error envelope."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.responses import JSONResponse

from climaprev.api.errors import ApplicationError, ErrorBody, ErrorEnvelope, RateLimitExceeded
from climaprev.application.errors import (
    DependencyUnavailable,
    LocationNotFound,
    ProviderPermanentError,
    ProviderTransientError,
    WeatherDataInvalid,
    WeatherProviderUnavailable,
)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        code, message = _validation_error(error)
        return _error_response(request, 422, code, message)

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(
        request: Request,
        error: ValidationError,
    ) -> JSONResponse:
        code, message = _validation_error(error)
        return _error_response(request, 422, code, message)

    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, error: ApplicationError) -> JSONResponse:
        if error.status_code == 422 and error.code in {
            "INVALID_LOCATION_INPUT",
            "INVALID_PERIOD",
            "INVALID_TEMPERATURE_UNIT",
        }:
            return _error_response(request, 422, error.code, error.message)
        return _error_response(request, 500, "INTERNAL_ERROR", "internal server error")

    @app.exception_handler(LocationNotFound)
    async def location_not_found_handler(request: Request, error: LocationNotFound) -> JSONResponse:
        return _error_response(request, 404, "LOCATION_NOT_FOUND", "location was not found")

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, error: RateLimitExceeded) -> JSONResponse:
        return _error_response(
            request,
            429,
            "RATE_LIMIT_EXCEEDED",
            "rate limit exceeded",
            headers={"Retry-After": str(error.retry_after_seconds)},
        )

    @app.exception_handler(WeatherDataInvalid)
    async def weather_data_handler(request: Request, error: WeatherDataInvalid) -> JSONResponse:
        return _error_response(request, 502, "WEATHER_DATA_INVALID", "weather data was invalid")

    @app.exception_handler(ProviderPermanentError)
    async def provider_rejected_handler(
        request: Request, error: ProviderPermanentError
    ) -> JSONResponse:
        return _error_response(
            request, 502, "WEATHER_PROVIDER_REJECTED", "weather provider rejected the request"
        )

    @app.exception_handler(ProviderTransientError)
    @app.exception_handler(WeatherProviderUnavailable)
    async def weather_unavailable_handler(
        request: Request,
        error: ProviderTransientError | WeatherProviderUnavailable,
    ) -> JSONResponse:
        return _error_response(
            request,
            503,
            "WEATHER_PROVIDER_UNAVAILABLE",
            "weather provider is unavailable",
        )

    @app.exception_handler(DependencyUnavailable)
    async def dependency_handler(request: Request, error: DependencyUnavailable) -> JSONResponse:
        return _error_response(request, 503, "DEPENDENCY_UNAVAILABLE", "dependency is unavailable")

    @app.exception_handler(Exception)
    async def internal_error_handler(request: Request, error: Exception) -> JSONResponse:
        return _error_response(request, 500, "INTERNAL_ERROR", "internal server error")


def _validation_error(error: RequestValidationError | ValidationError) -> tuple[str, str]:
    locations = [item.get("loc", ()) for item in error.errors()]
    if any("temperature_unit" in location for location in locations):
        return "INVALID_TEMPERATURE_UNIT", "temperature_unit must be celsius or fahrenheit"
    if any("start_date" in location or "end_date" in location for location in locations):
        return "INVALID_PERIOD", "date period is invalid"
    messages = [str(item.get("msg", "")) for item in error.errors()]
    if any("date period" in message or "end_date" in message for message in messages):
        return "INVALID_PERIOD", "date period is invalid"
    return "INVALID_LOCATION_INPUT", "location input is invalid"


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    request.state.error_code = code
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=status_code,
        content=ErrorEnvelope(
            error=ErrorBody(code=code, message=message, request_id=request_id)
        ).model_dump(),
        headers=headers,
    )
