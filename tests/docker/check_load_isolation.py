"""Static contract for an isolated, mock-only load profile."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    assert "redis-load:6379" in compose
    assert "redis-load:" in compose
    assert "load-backend:" in compose and "load-edge:" in compose
    assert "CLIMAPREV_GEOCODING_BASE_URL: http://provider-mock:8080" in compose
    assert "CLIMAPREV_FORECAST_BASE_URL: http://provider-mock:8080" in compose
    assert "CLIMAPREV_INMET_ALERTS_BASE_URL: ${CLIMAPREV_INMET_ALERTS_BASE_URL:-http://provider-mock:8080}" in compose
    assert "depends_on:\n      redis-load:" in compose
    assert "REDIS_URL: redis://redis:6379/0" not in compose.split("  app-load:", 1)[1]


if __name__ == "__main__":
    check()
    print("Load profile isolation contract: OK.")
