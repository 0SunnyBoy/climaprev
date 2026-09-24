"""Isolated synthetic settings without inventing deployment environments."""

from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from climaprev.config import Settings


def isolated_settings(**overrides: object) -> Settings:
    nonce = uuid4().hex
    with TemporaryDirectory(prefix="climaprev-test-key-") as directory:
        key = Path(directory) / "synthetic-hmac.key"
        key.write_text(nonce * 2)
        return Settings(**{
            "environment": "test",
            "client_ip_hmac_key_file": key,
            "forecast_base_url": f"https://forecast-{nonce}.test",
            "geocoding_base_url": f"https://geocoding-{nonce}.test",
            "inmet_alerts_base_url": f"https://alerts-{nonce}.test",
            **overrides,
        })
