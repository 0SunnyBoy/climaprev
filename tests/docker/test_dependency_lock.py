import re
from pathlib import Path

import pytest


@pytest.mark.parametrize("filename", ["requirements.lock", "requirements-build.lock"])
def test_locks_pin_every_distribution_with_hashes_and_no_private_sources(filename: str) -> None:
    text = Path(filename).read_text()
    entries = [entry for entry in text.splitlines() if entry and not entry.startswith((" ", "#"))]
    assert entries
    assert all(re.fullmatch(r"[A-Za-z0-9_.-]+==[^\s;]+ \\", entry) for entry in entries)
    assert len(re.findall(r"--hash=sha256:[a-f0-9]{64}", text)) >= len(entries)
    assert not any(value in text for value in ("https://", "http://", "file://", "/home/", "@"))
    if filename == "requirements.lock":
        assert not any(
            re.match(r"(pytest|ruff|mypy|locust|setuptools|wheel)==", entry) for entry in entries
        )
