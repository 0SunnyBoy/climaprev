"""Reproducible browser acceptance gate for the public frontend boundary."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import Dialog, Page, sync_playwright

MALICIOUS_TEXT = "<img src=x onerror=alert('SYNTHETIC-XSS')>"


def _origin(url: str) -> tuple[str, str | None, int | None]:
    parsed = urlparse(url)
    default_port = {"http": 80, "https": 443}.get(parsed.scheme)
    return parsed.scheme, parsed.hostname, parsed.port or default_port


def _result_payload() -> dict[str, object]:
    return {
        "request_id": "browser-synthetic",
        "disclaimer": MALICIOUS_TEXT,
        "location": {
            "name": MALICIOUS_TEXT,
            "latitude": -1.4558,
            "longitude": -48.4902,
            "timezone": "America/Belem",
            "source": "synthetic",
        },
        "period": {"start_date": "2030-01-01", "end_date": "2030-01-01"},
        "temperature_unit": "celsius",
        "days": [{
            "date": "2030-01-01", "temperature_min": 20, "temperature_max": 30,
            "temperature_mean": 25, "humidity_mean_pct": 70, "precipitation_sum_mm": 0,
            "precipitation_probability_max_pct": 10, "precipitation_max_hourly_mm": 0,
            "wind_max_kmh": 15, "wind_gust_max_kmh": 20, "weather_code": 1,
        }],
        "forecast_risk": {
            "level": "low", "method": "reference-v1", "policy_version": "reference-v1",
            "conditions": [{
                "type": "strong_wind_proxy", "severity": "low", "unit": "km/h",
                "value": 20, "reason": MALICIOUS_TEXT,
            }],
        },
        "data_quality": {"is_stale": False, "completeness": "complete", "missing_fields": []},
        "source": {"provider": "synthetic", "fetched_at": "2030-01-01T12:00:00Z"},
        "official_alerts": {"status": "not_configured", "items": []},
    }


def _check_accessibility(page: Page) -> None:
    """Run deterministic accessibility smoke checks in the real browser."""
    assert page.locator("html").get_attribute("lang") == "pt-BR"
    assert page.locator("main").count() == 1
    assert page.locator(".skip-link").get_attribute("href") == "#consulta"
    assert page.locator("#consulta").get_attribute("tabindex") == "-1"
    assert page.locator("label[for='location-mode']").count() == 1
    assert page.locator("label[for='location_text']").count() == 1
    assert page.locator("#query-form input, #query-form select").count() == page.locator(
        "#query-form label[for]"
    ).count()

    page.locator(".skip-link").focus()
    page.locator(".skip-link").press("Enter")
    assert page.evaluate("document.activeElement.id") == "consulta"

    page.fill("#location_text", "Belem")
    page.locator(".location-suggestion").first.wait_for(state="visible")
    input_locator = page.locator("#location_text")
    assert input_locator.get_attribute("role") == "combobox"
    assert input_locator.get_attribute("aria-expanded") == "true"
    assert input_locator.get_attribute("aria-controls") == "location-suggestions"
    assert page.locator("#location-suggestions").get_attribute("role") == "listbox"
    assert page.locator("#location-suggestions [role='option']").count() > 0

    input_locator.press("ArrowDown")
    active_id = input_locator.get_attribute("aria-activedescendant")
    assert active_id is not None
    assert page.locator(f"#{active_id}").get_attribute("aria-selected") == "true"
    input_locator.press("Enter")
    assert page.locator("#location-suggestions").count() == 0
    assert input_locator.get_attribute("aria-expanded") == "false"
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def _check_theme_toggle(page: Page) -> None:
    """Verify the theme control changes, exposes and persists its state."""
    toggle = page.locator(".theme-toggle")
    assert toggle.get_attribute("aria-pressed") == "false"
    assert page.evaluate("document.documentElement.dataset.theme") == "light"

    toggle.click()
    assert toggle.get_attribute("aria-pressed") == "true"
    assert "modo claro" in (toggle.get_attribute("aria-label") or "")
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"
    assert page.evaluate("localStorage.getItem('climaprev-theme')") == "dark"

    page.reload(wait_until="networkidle")
    toggle = page.locator(".theme-toggle")
    assert toggle.get_attribute("aria-pressed") == "true"
    assert page.evaluate("document.documentElement.dataset.theme") == "dark"

    toggle.click()
    assert toggle.get_attribute("aria-pressed") == "false"
    assert "modo escuro" in (toggle.get_attribute("aria-label") or "")
    assert page.evaluate("document.documentElement.dataset.theme") == "light"
    page.evaluate("localStorage.clear()")


def _install_ca(ca_file: Path, profile: Path) -> None:
    if os.name == "nt":
        raise RuntimeError("HTTPS browser validation requires NSS certutil on a Linux test runner")
    certutil = shutil.which("certutil")
    if certutil is None:
        raise RuntimeError("certutil is required when --ca-file is supplied")
    database = f"sql:{profile}"
    subprocess.run(
        [certutil, "-N", "-d", database, "--empty-password"],
        check=True,
        capture_output=True,
    )
    subprocess.run([
        certutil,
        "-A",
        "-d",
        database,
        "-n",
        "climaprev-test-ca",
        "-t",
        "C,,",
        "-a",
        "-i",
        str(ca_file),
    ], check=True, capture_output=True)


def check(base_url: str, ca_file: Path | None, executable_path: Path | None) -> None:
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("--base-url must be an absolute http:// or https:// URL")
    if parsed.scheme == "https" and ca_file is None:
        raise ValueError("HTTPS validation requires --ca-file; certificate checks stay enabled")

    with sync_playwright() as playwright:
        browser = None
        context = None
        profile = None
        try:
            if ca_file is None:
                launch_options = {"headless": True}
                if executable_path is not None:
                    launch_options["executable_path"] = str(executable_path)
                browser = playwright.chromium.launch(**launch_options)
                context = browser.new_context()
            else:
                profile = Path(tempfile.mkdtemp(prefix="climaprev-firefox-profile-"))
                _install_ca(ca_file, profile)
                context = playwright.firefox.launch_persistent_context(str(profile), headless=True)

            errors: list[str] = []
            network_urls: list[str] = []
            page: Page = context.new_page()
            page.on("pageerror", lambda error: errors.append(f"pageerror: {error}"))
            page.on("request", lambda request: network_urls.append(request.url))
            def reject_dialog(dialog: Dialog) -> None:
                errors.append(f"unexpected dialog: {dialog.type}")
                dialog.dismiss()

            page.on("dialog", reject_dialog)
            page.on(
                "console",
                lambda message: errors.append(f"console {message.type}: {message.text}")
                if message.type == "error"
                else None,
            )
            page.route("**/api/v1/risk", lambda route: route.fulfill(
                status=200, content_type="application/json", body=json.dumps(_result_payload())
            ))
            page.route("**/api/v1/locations/search**", lambda route: route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps([{
                    "name": "Belém, Pará, Brasil",
                    "latitude": -1.4558,
                    "longitude": -48.4902,
                    "timezone": "America/Belem",
                    "source": "synthetic",
                }]),
            ))
            page.add_init_script(
                "if (!window.localStorage.getItem('climaprev-theme')) "
                "window.localStorage.setItem('climaprev-theme', 'light')"
            )
            response = page.goto(base_url.rstrip("/") + "/", wait_until="networkidle")
            assert response is not None and response.status == 200
            assert page.title() == "Clima Prev · Previsão com contexto"
            assert page.locator("link[rel='stylesheet']").count() == 1
            background = page.evaluate("getComputedStyle(document.documentElement).backgroundColor")
            assert background != "rgb(255, 255, 255)"
            _check_accessibility(page)
            _check_theme_toggle(page)

            page.select_option("#location-mode", "coordinates")
            page.fill("#latitude", "-1.4558")
            page.fill("#longitude", "-48.4902")
            page.fill("#start_date", "2030-01-01")
            page.click("button[type='submit']")
            page.locator("#result").wait_for(state="visible")
            result_text = page.locator("#result").inner_text()
            assert MALICIOUS_TEXT in result_text
            assert page.locator("#result img").count() == 0
            assert page.locator("#result script").count() == 0
            assert page.locator("#result [onerror]").count() == 0
            assert any(urlparse(url).path == "/api/v1/risk" for url in network_urls)
            http_origins = {
                _origin(url)
                for url in network_urls
                if urlparse(url).scheme in {"http", "https"}
            }
            assert http_origins == {_origin(base_url)}, http_origins
            assert page.evaluate("localStorage.length + sessionStorage.length") == 0
            assert context.cookies() == []
            assert not errors, "browser emitted errors: " + "; ".join(errors)
        finally:
            if context is not None:
                context.close()
            if browser is not None:
                browser.close()
            if profile is not None:
                shutil.rmtree(profile, ignore_errors=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--ca-file", type=Path)
    parser.add_argument("--executable-path", type=Path)
    args = parser.parse_args()
    check(args.base_url, args.ca_file, args.executable_path)
    print("Frontend browser acceptance: CSS, accessibility, same-origin app and inert synthetic content OK.")
