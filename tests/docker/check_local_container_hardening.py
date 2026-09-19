#!/usr/bin/env python3
"""Validate the local Compose container-hardening contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "redis:7-alpine@sha256:" in compose
    assert "nginx:1.27-alpine@sha256:" in compose
    assert compose.count("<<: *hardened-service") == 6
    assert compose.count("no-new-privileges:true") == 1
    assert compose.count("- ALL") == 1
    assert "- CHOWN" in compose
    assert "- SETGID" in compose
    assert "- SETUID" in compose
    assert compose.count("read_only: true") == 2
    assert "- /etc/nginx/conf.d" in compose
    assert "- /var/cache/nginx" in compose
    assert "- /data" in compose
    assert "internal: true" in compose
    assert "${CLIMAPREV_BACKEND_SUBNET:-172.31.0.0/24}" in compose


if __name__ == "__main__":
    check()
    print("Local container-hardening contract: OK.")
