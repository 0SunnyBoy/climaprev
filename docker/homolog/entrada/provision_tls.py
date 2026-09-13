"""Generate a private local test CA without changing OS or browser trust."""
import argparse
import shutil
import subprocess
import tempfile
from pathlib import Path


def provision(directory: Path) -> None:
    names = ('ca.key', 'ca.crt', 'server.key', 'server.crt')
    if any((directory / name).exists() for name in names):
        raise FileExistsError('TLS material already exists; it will not be overwritten')
    if directory.stat().st_mode & 0o077:
        raise ValueError('Local credential directory must be private (0700)')
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
            (directory / name).chmod(0o600 if name == 'ca.key' else 0o444)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    provision(args.directory)
    print('Local TLS certificate and CA created; no global trust was changed.')
