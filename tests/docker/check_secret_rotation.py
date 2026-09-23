"""Synthetic rotation contract; never reads a real project secret."""

import runpy
import tempfile
from pathlib import Path

PROVISION = Path(__file__).resolve().parents[2] / "docker/homolog/provision.py"


def check() -> None:
    provision = runpy.run_path(str(PROVISION))["provision"]
    with tempfile.TemporaryDirectory(prefix="climaprev-security-rotation-") as temporary:
        root = Path(temporary)
        first = root / "first"
        second = root / "second"
        provision(first, 60, 60, 60, "production")
        provision(second, 60, 60, 60, "production")
        assert (first / "redis.password").read_text() != (second / "redis.password").read_text()
        assert (first / "client-ip-hmac.key").read_text() != (second / "client-ip-hmac.key").read_text()
        assert (first / "redis.acl").read_text() != (second / "redis.acl").read_text()


if __name__ == "__main__":
    check()
    print("Synthetic secret rotation contract: OK.")
