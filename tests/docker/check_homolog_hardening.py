"""Check real homologation container privileges without reading secret values."""

import json
import subprocess

PREFIX = "climaprev-homolog-"
EXPECTED_USERS = {
    "redis": "999:1000",
    "app": "10001:10001",
    "collector": "10001:10001",
    "entrada": "101:101",
}
EXPECTED_SECRETS = {
    "redis": {"/run/secrets/redis_acl"},
    "app": {"/run/secrets/redis_password", "/run/secrets/client_ip_hmac_key"},
    "collector": set(),
    "entrada": {"/run/secrets/tls_certificate", "/run/secrets/tls_key"},
}


def inspect(service: str) -> dict:
    payload = subprocess.check_output(
        ["docker", "inspect", f"{PREFIX}{service}-1", "--format", "{{json .}}"],
        text=True,
    )
    return json.loads(payload)


def can_read(service: str, secret: str) -> bool:
    result = subprocess.run(
        ["docker", "exec", f"{PREFIX}{service}-1", "sh", "-c", f"test -r {secret}"],
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def check() -> None:
    all_secrets = set().union(*EXPECTED_SECRETS.values())
    for service, user in EXPECTED_USERS.items():
        data = inspect(service)
        host = data["HostConfig"]
        destinations = {mount["Destination"] for mount in data["Mounts"]}
        mounted_secrets = {path for path in destinations if path.startswith("/run/secrets/")}
        assert data["Config"]["User"] == user, service
        assert host["ReadonlyRootfs"] is True, service
        assert "ALL" in host["CapDrop"], service
        assert "no-new-privileges:true" in host["SecurityOpt"], service
        assert mounted_secrets == EXPECTED_SECRETS[service], service
        for secret in all_secrets:
            assert can_read(service, secret) == (secret in EXPECTED_SECRETS[service]), (
                service,
                secret,
            )
    print("Homolog hardening: users, read-only filesystems, capabilities and secret mounts OK.")


if __name__ == "__main__":
    check()
