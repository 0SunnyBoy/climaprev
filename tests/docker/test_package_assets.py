import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def test_built_wheel_excludes_web_assets(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    shutil.copy("pyproject.toml", source)
    shutil.copytree("src", source / "src")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "--isolated",
            "wheel",
            "--no-build-isolation",
            "--no-deps",
            "--wheel-dir",
            str(tmp_path / "wheels"),
            str(source),
        ],
        check=True,
        capture_output=True,
    )
    wheel = next((tmp_path / "wheels").glob("climaprev-*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        assert any(name.startswith("climaprev/") and name.endswith(".py") for name in names)
        assert not any(name.startswith("climaprev/web/") for name in names)
