"""Use the existing Windows ACL/TLS provisioner with an isolated OpenSSL command."""
import importlib.util
import subprocess
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location('provision_tls', 'docker/homolog/entrada/provision_tls.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_run = subprocess.run


def run(command, **kwargs):
    if command[0] == 'openssl':
        directory = Path(kwargs['cwd']).resolve()
        command = ['docker', 'run', '--rm', '--mount',
                   f'type=bind,source={directory},target=/cert', '-w', '/cert',
                   'climaprev-openssl-test:local', *command]
    return original_run(command, **kwargs)


module.subprocess.run = run
module.provision(Path(sys.argv[1] if len(sys.argv) > 1 else '.homolog'))
print('Private local TLS material generated; Windows ACL enforced; no trust store changed.')
