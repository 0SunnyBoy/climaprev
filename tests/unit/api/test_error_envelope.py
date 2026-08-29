from climaprev.api.errors import ApplicationError, ErrorBody, ErrorEnvelope


def test_error_envelope_serializes_request_id() -> None:
    envelope = ErrorEnvelope(
        error=ErrorBody(
            code="INVALID_TEMPERATURE_UNIT",
            message="temperature_unit must be celsius or fahrenheit",
            request_id="req-123",
        )
    )

    assert envelope.model_dump() == {
        "error": {
            "code": "INVALID_TEMPERATURE_UNIT",
            "message": "temperature_unit must be celsius or fahrenheit",
            "request_id": "req-123",
        }
    }


def test_application_error_preserves_http_response_fields() -> None:
    error = ApplicationError(
        code="INVALID_TEMPERATURE_UNIT",
        message="temperature_unit must be celsius or fahrenheit",
        status_code=422,
    )

    assert error.code == "INVALID_TEMPERATURE_UNIT"
    assert error.message == "temperature_unit must be celsius or fahrenheit"
    assert error.status_code == 422
