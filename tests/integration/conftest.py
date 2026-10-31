"""Anchor API clock to the dates used by the deterministic provider fixtures."""

from datetime import date

import pytest


@pytest.fixture(autouse=True)
def public_forecast_fixture_clock(monkeypatch):
    monkeypatch.setattr("climaprev.api.forecast_window.utc_today", lambda: date(2026, 8, 28))
