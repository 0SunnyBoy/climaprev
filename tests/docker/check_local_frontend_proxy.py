"""Validate the local frontend proxy identity configuration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check() -> None:
    nginx = (ROOT / "frontend/nginx.conf").read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert nginx.count("proxy_set_header X-Forwarded-For $remote_addr;") == 4
    assert nginx.count("proxy_set_header X-Forwarded-Proto $scheme;") == 4
    assert "$proxy_add_x_forwarded_for" not in nginx
    assert "expires 1h;" in nginx
    assert "expires -1;" in nginx
    assert "client_max_body_size 16k;" in nginx
    assert "location = /api/v1/risk" in nginx
    assert "location = /api/v1/locations/search" in nginx
    assert "location / { return 404; }" in nginx
    assert "access_log off;" in nginx
    assert "limit_except GET POST { deny all; }" in nginx
    assert "CLIMAPREV_TRUSTED_PROXY_IPS: ${CLIMAPREV_TRUSTED_PROXY_IPS:-172.32.0.10}" in compose
    assert "ipv4_address: ${CLIMAPREV_FRONTEND_IP:-172.32.0.10}" in compose
    assert "subnet: ${CLIMAPREV_LOCAL_SUBNET:-172.32.0.0/24}" in compose


if __name__ == "__main__":
    check()
    print("Local frontend proxy identity configuration: OK.")
