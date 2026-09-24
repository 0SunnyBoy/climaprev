"""Generate a private local test CA without changing OS or browser trust."""
import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def _windows_identity() -> str:
    try:
        result = subprocess.run(
            ["whoami"], check=True, capture_output=True, text=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        raise RuntimeError("Unable to determine the current Windows identity") from error
    identity = result.stdout.strip()
    if not identity:
        raise RuntimeError("Unable to determine the current Windows identity")
    return identity


def _restrict_windows_acl(path: Path, *, directory: bool) -> None:
    permission = "(OI)(CI)F" if directory else "F"
    principals = (
        _windows_identity(),
        "*S-1-5-18",  # Local System
        "*S-1-5-32-544",  # Built-in Administrators
    )
    grants = [f"{principal}:{permission}" for principal in principals]
    try:
        subprocess.run(
            [
                "icacls",
                str(path),
                "/inheritance:r",
                "/grant:r",
                *grants,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        raise RuntimeError(f"Unable to secure Windows ACL for {path}") from error


def _ensure_private_directory(directory: Path) -> None:
    if os.name == "nt":
        _restrict_windows_acl(directory, directory=True)
    elif directory.stat().st_mode & 0o077:
        raise ValueError("Local credential directory must be private (0700)")


def _secure_file(path: Path, mode: int) -> None:
    path.chmod(mode)
    if os.name == "nt":
        _restrict_windows_acl(path, directory=False)


def provision(directory: Path) -> None:
    names = ('ca.key', 'ca.crt', 'server.key', 'server.crt')
    if any((directory / name).exists() for name in names):
        raise FileExistsError('TLS material already exists; it will not be overwritten')
    _ensure_private_directory(directory)
    with tempfile.TemporaryDirectory(dir=directory) as temporary:
        target = Path(temporary)
        commands = [
            ['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-keyout', 'ca.key',
             '-out', 'ca.crt', '-sha256', '-days', '30', '-subj', '/CN=ClimaPrev Local Test CA',
             '-addext', 'basicConstraints=critical,CA:TRUE',
             '-addext', 'keyUsage=critical,keyCertSign,cRLSign'],
            ['openssl', 'req', '-newkey', 'rsa:2048', '-nodes', '-keyout', 'server.key',
             '-out', 'server.csr', '-subj', '/CN=localhost'],
            ['openssl', 'x509', '-req', '-in', 'server.csr', '-CA', 'ca.crt', '-CAkey', 'ca.key',
             '-CAcreateserial', '-out', 'server.crt', '-days', '30', '-sha256', '-extfile', 'leaf.cnf'],
        ]
        (target / 'leaf.cnf').write_text('subjectAltName=DNS:localhost,IP:127.0.0.1\n'
                                      'basicConstraints=critical,CA:FALSE\n'
                                      'keyUsage=critical,digitalSignature,keyEncipherment\n'
                                      'extendedKeyUsage=serverAuth\n')
        for command in commands:
            subprocess.run(command, cwd=target, check=True, capture_output=True)
        for name in names:
            shutil.move(str(target / name), directory / name)
            _secure_file(directory / name, 0o600 if name == 'ca.key' else 0o444)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    provision(args.directory)
    print('Local TLS certificate and CA created; no global trust was changed.')
