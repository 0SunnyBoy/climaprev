"""BUILD-01: explicit Docker gate; run at repo root, using only synthetic secrets.

Builds a context-probe and runtime in a temporary tracked-file fixture. Examines
all saved image layers, not just the final filesystem. Needs a working engine.
"""

import io
import json
import shutil
import subprocess
import tarfile
import tempfile
import uuid
from pathlib import Path

SENTINEL = b"SYNTHETIC-BUILD-SECRET-SENTINEL"


def check_layers(image: str, directory: Path, sentinel: bytes) -> None:
    saved = directory / "image.tar"
    subprocess.run(["docker", "image", "save", "-o", str(saved), image], check=True)
    with tarfile.open(saved) as archive:
        manifest_file = archive.extractfile("manifest.json")
        assert manifest_file is not None
        manifests = json.load(manifest_file)
        for layer in manifests[0]["Layers"]:
            layer_file = archive.extractfile(layer)
            assert layer_file is not None
            with tarfile.open(fileobj=io.BytesIO(layer_file.read())) as contents:
                for member in contents:
                    if member.isfile():
                        name = Path(member.name)
                        assert not name.name.startswith(".env") or member.name == ".env.example"
                        value = contents.extractfile(member)
                        assert value is not None
                        assert sentinel not in value.read(), member.name


def main() -> None:
    repo = Path.cwd()
    # A unique suffix distinguishes injected contents from the test source itself.
    sentinel = SENTINEL + uuid.uuid4().hex.encode()
    with tempfile.TemporaryDirectory(prefix="climaprev-build-secrets-") as temporary:
        directory = Path(temporary)
        source = directory / "context"
        source.mkdir()
        tracked = subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
        for name in tracked:
            if not name or Path(name).name.startswith(".env") and name != ".env.example":
                continue
            if name in ("Dockerfile", ".dockerignore", "pyproject.toml", "README.md",
                        "requirements.lock", "requirements-build.lock", ".env.example") \
                    or name.startswith(("src/", "tests/", "docs/")):
                target = source / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(repo / name, target)
        for folder in (source, source / "src/climaprev", source / "tests", source / "docs"):
            folder.mkdir(parents=True, exist_ok=True)
            for name in (".env.production", ".env.local", "private.key", "redis.password"):
                (folder / name).write_bytes(sentinel)
        dockerfile = source / "Dockerfile"
        dockerfile.write_text(dockerfile.read_text() + "\nFROM scratch AS context-probe\nCOPY . /\n")
        for target in ("context-probe", "runtime"):
            tag = f"climaprev-secret-check:{uuid.uuid4().hex}"
            try:
                subprocess.run(["docker", "build", "--load", "--target", target, "-t", tag,
                                str(source)], check=True)
                check_layers(tag, directory, sentinel)
                if target == "runtime":
                    subprocess.run([
                        "docker", "run", "--rm", "--pids-limit", "256",
                        "--network", "none", "--read-only",
                        "--mount", (f"type=bind,src={repo / 'tests/docker/check_runtime_image.py'},"
                                    "dst=/tmp/check_runtime_image.py,readonly"),
                        tag, "python", "/tmp/check_runtime_image.py",
                    ], check=True)
            finally:
                subprocess.run(["docker", "image", "rm", tag], check=False,
                               capture_output=True)
    print("BUILD-01: synthetic secrets absent from effective context and runtime layers")


if __name__ == "__main__":
    main()
