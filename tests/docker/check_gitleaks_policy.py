"""Prove that the pinned Gitleaks policy detects synthetic credentials."""

from __future__ import annotations

import argparse
import secrets
import string
import subprocess
import tempfile
from pathlib import Path

IMAGE = (
    "zricethezav/gitleaks@sha256:"
    "c00b6bd0aeb3071cbcb79009cb16a60dd9e0a7c60e2be9ab65d25e6bc8abbb7f"
)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_LINE = (
    "CLIMAPREV_GEOCODING_BASE_URL=https://geocoding-api.open-meteo.com\n"
)


def _scan(directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--mount",
            f"type=bind,source={PROJECT_ROOT},target=/repo,readonly",
            "--mount",
            f"type=bind,source={directory},target=/fixture,readonly",
            IMAGE,
            "dir",
            "--redact",
            "--config",
            "/repo/.gitleaks.toml",
            "--gitleaks-ignore-path",
            "/repo/.gitleaksignore",
            "/fixture",
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def _assert_scan(directory: Path, expected_code: int, token: str | None = None) -> None:
    result = _scan(directory)
    if token is not None and token in (result.stdout + result.stderr):
        raise AssertionError("Gitleaks output disclosed the synthetic token")
    if result.returncode != expected_code:
        raise AssertionError(
            f"Gitleaks returned {result.returncode}, expected {expected_code}; "
            f"redacted output: {(result.stdout + result.stderr)[-1000:]}"
        )


def check() -> None:
    with tempfile.TemporaryDirectory(prefix="climaprev-gitleaks-") as raw_directory:
        directory = Path(raw_directory)
        example = directory / ".env.example"
        example.write_text(PUBLIC_LINE, encoding="utf-8")
        _assert_scan(directory, 0)

        alphabet = string.ascii_letters + string.digits
        token = "ghp_" + "".join(secrets.choice(alphabet) for _ in range(36))
        example.write_text(PUBLIC_LINE + f"SYNTHETIC_TOKEN={token}\n", encoding="utf-8")
        _assert_scan(directory, 1, token)

        example.unlink()
        (directory / "credentials.txt").write_text(f"SYNTHETIC_TOKEN={token}\n", encoding="utf-8")
        _assert_scan(directory, 1, token)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    check()
    print("Gitleaks policy: public example accepted; synthetic tokens blocked and redacted.")
