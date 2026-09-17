"""Explicit build gate: two clean installations, not part of the offline pytest suite."""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


def check() -> None:
    lock = Path("requirements.lock").resolve()
    expected = {
        name.lower().replace("_", "-"): version
        for name, version in re.findall(
            r"^([A-Za-z0-9_.-]+)==([^\s;\\]+)", lock.read_text(), re.MULTILINE
        )
    }
    results = []
    with tempfile.TemporaryDirectory() as directory:
        for number in range(2):
            target = Path(directory) / str(number)
            subprocess.run([sys.executable, "-m", "venv", str(target)], check=True)
            python = str(target / "bin/python")
            subprocess.run(
                [
                    python,
                    "-m",
                    "pip",
                    "--isolated",
                    "install",
                    "--no-cache-dir",
                    "--index-url",
                    "https://pypi.org/simple",
                    "--require-hashes",
                    "-r",
                    str(lock),
                ],
                check=True,
                stdout=subprocess.PIPE,
            )
            subprocess.run([python, "-m", "pip", "check"], check=True, stdout=subprocess.PIPE)
            code = (
                "import importlib.metadata,json; print(json.dumps({d.metadata['Name'].lower().replace('_','-'):"
                "d.version for d in importlib.metadata.distributions() if d.metadata['Name'] != 'pip'}))"
            )
            installed = json.loads(subprocess.check_output([python, "-c", code], text=True))
            assert installed == expected
            results.append(installed)
    assert results[0] == results[1]
    print(
        json.dumps(
            {"installations": 2, "dependencies": len(expected), "versions": results[0]},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    check()
