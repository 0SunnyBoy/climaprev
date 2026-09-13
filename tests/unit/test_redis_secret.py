from pathlib import Path

import pytest
from pydantic import ValidationError

from climaprev.config import Settings


def test_reads_secret_file_without_serializing_password(tmp_path: Path) -> None:
    secret = tmp_path / "password"
    secret.write_text("SecretSentinel\n")
    settings = Settings(redis_password_file=secret)
    assert settings.redis_password == "SecretSentinel"
    assert "SecretSentinel" not in repr(settings)
    assert "SecretSentinel" not in settings.model_dump_json()


@pytest.mark.parametrize("contents", [None, ""])
def test_missing_or_empty_secret_fails_with_sanitized_error(tmp_path: Path, contents) -> None:
    secret = tmp_path / "SecretPathSentinel"
    if contents is not None:
        secret.write_text(contents)
    with pytest.raises(ValidationError) as raised:
        Settings(redis_password_file=secret)
    assert "Redis secret file is missing, unreadable or empty" in str(raised.value)
    assert "SecretPathSentinel" not in str(raised.value)
