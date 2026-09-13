import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


def test_built_wheel_preserves_web_assets(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    shutil.copy("pyproject.toml", source)
    shutil.copytree("src", source / "src")
    web = source / "src/climaprev/web"
    web.mkdir(exist_ok=True)
    for extension in ("html", "css", "js"):
        (web / f"packaging-probe.{extension}").write_text("package asset fixture")
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
        for extension in ("html", "css", "js"):
            assert (
                archive.read(f"climaprev/web/packaging-probe.{extension}")
                == b"package asset fixture"
            )
