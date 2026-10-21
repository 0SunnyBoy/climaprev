"""Validate effective local Compose hardening, independent of service counts."""

import ipaddress
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def check() -> None:
    # Keep expanded configuration in memory: it may contain local environment values.
    compose = json.loads(subprocess.check_output(
        ["docker", "compose", "--profile", "*", "config", "--format", "json"],
        cwd=ROOT, text=True,
    ))
    services = compose["services"]
    assert re.fullmatch(r"redis:7-alpine@sha256:[0-9a-f]{64}", services["redis"]["image"])
    frontend = (ROOT / "frontend/Dockerfile").read_text(encoding="utf-8")
    assert re.search(r"(?m)^FROM nginx:[^\s]+@sha256:[0-9a-f]{64}$", frontend)

    for service in services.values():
        assert "no-new-privileges:true" in service.get("security_opt", [])
        assert service.get("cap_drop") == ["ALL"]

    for name in ("redis", "frontend", "redis-load"):
        service = services[name]
        assert service.get("read_only") is True
        assert set(service.get("cap_add", [])) == {"CHOWN", "SETGID", "SETUID"}
    for name in ("redis", "redis-load"):
        assert "/data" in services[name]["tmpfs"]
    assert {"/etc/nginx/conf.d", "/var/cache/nginx"} <= set(services["frontend"]["tmpfs"])

    backend = compose["networks"]["backend"]
    assert backend.get("internal") is True
    assert backend["ipam"]["config"]
    assert all(ipaddress.ip_network(item["subnet"]).is_private
               for item in backend["ipam"]["config"])


if __name__ == "__main__":
    check()
    print("Local container-hardening contract: OK.")
