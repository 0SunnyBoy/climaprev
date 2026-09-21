"""Validate the local frontend proxy identity configuration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check() -> None:
    nginx = (ROOT / "docker/frontend/nginx.conf").read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert nginx.count("proxy_set_header X-Forwarded-For $remote_addr;") == 3
    assert nginx.count("proxy_set_header X-Forwarded-Proto $scheme;") == 3
    assert "$proxy_add_x_forwarded_for" not in nginx
    assert "expires 1h;" in nginx
    assert "expires -1;" in nginx
    assert "CLIMAPREV_TRUSTED_PROXY_IPS: ${CLIMAPREV_TRUSTED_PROXY_IPS:-172.32.0.10}" in compose
    assert "ipv4_address: ${CLIMAPREV_FRONTEND_IP:-172.32.0.10}" in compose
    assert "subnet: ${CLIMAPREV_LOCAL_SUBNET:-172.32.0.0/24}" in compose


if __name__ == "__main__":
    check()
    print("Local frontend proxy identity configuration: OK.")
