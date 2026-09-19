#!/usr/bin/env python3

from climaprev.config import Settings
from climaprev.main import create_app


def test_api_documentation_is_enabled_in_development() -> None:
    app = create_app(Settings(environment="development"))

    assert app.docs_url == "/docs"
    assert app.redoc_url == "/redoc"
    assert app.openapi_url == "/openapi.json"


def test_api_documentation_is_disabled_outside_development() -> None:
    app = create_app(Settings(environment="production"))

    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None
