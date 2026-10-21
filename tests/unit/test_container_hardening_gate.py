"""Security regressions for the effective-Compose gate; no Docker required."""

import copy
import json

import pytest
from tests.docker import check_local_container_hardening as gate


@pytest.fixture
def configuration(tmp_path, monkeypatch):
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "Dockerfile").write_text("FROM nginx:1.27-alpine@sha256:" + "0" * 64 + "\n")
    common = {"security_opt": ["no-new-privileges:true"], "cap_drop": ["ALL"],
              "read_only": True, "cap_add": ["CHOWN", "SETGID", "SETUID"]}
    redis = {**common, "image": "redis:7-alpine@sha256:" + "0" * 64, "tmpfs": ["/data"]}
    data = {"services": {"redis": copy.deepcopy(redis), "redis-load": copy.deepcopy(redis),
                         "frontend": {**common, "tmpfs": ["/etc/nginx/conf.d", "/var/cache/nginx"]},
                         "app": {"security_opt": ["no-new-privileges:true"], "cap_drop": ["ALL"]}},
            "networks": {"backend": {"internal": True,
                                      "ipam": {"config": [{"subnet": "172.31.0.0/24"}]}}}}
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate.subprocess, "check_output", lambda *args, **kwargs: json.dumps(data))
    return data


def test_hardened_services_do_not_depend_on_a_fixed_service_count(configuration):
    configuration["services"]["extra-worker"] = {
        "security_opt": ["no-new-privileges:true"], "cap_drop": ["ALL"],
    }
    gate.check()


@pytest.mark.parametrize("control", [
    "security_opt", "cap_drop", "read_only", "cap_add", "tmpfs", "internal", "redis_image",
])
def test_missing_protections_cannot_pass_the_gate(configuration, control):
    if control == "internal":
        configuration["networks"]["backend"]["internal"] = False
    elif control == "redis_image":
        configuration["services"]["redis"]["image"] = "redis:7-alpine"
    else:
        configuration["services"]["frontend"].pop(control)
    with pytest.raises((AssertionError, KeyError)):
        gate.check()
