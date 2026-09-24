"""Read-only host-side topology proof; never prints expanded configuration."""

import argparse
import json
import subprocess


def inspect(kind: str, name: str, template: str):
    return json.loads(
        subprocess.check_output(["docker", kind, "inspect", name, "--format", template], text=True)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file")
    args = parser.parse_args()
    for service in ("app", "redis"):
        ports = json.loads(
            subprocess.check_output(
                [
                    "docker",
                    "inspect",
                    f"climaprev-homolog-{service}-1",
                    "--format",
                    "{{json .HostConfig.PortBindings}}",
                ],
                text=True,
            )
        )
        assert not ports
    assert inspect("network", "climaprev-homolog_cache", "{{json .Internal}}") is True
    peers = inspect("network", "climaprev-homolog_cache", "{{json .Containers}}")
    assert {value["Name"] for value in peers.values()} == {
        "climaprev-homolog-app-1",
        "climaprev-homolog-redis-1",
    }
    compose_command = ["docker", "compose"]
    if args.env_file:
        compose_command.extend(["--env-file", args.env_file])
    configuration = json.loads(
        subprocess.check_output(
            [*compose_command, "-f", "docker-compose.homolog.yml", "config", "--format", "json"],
            text=True,
        )
    )
    assert not {"load", "app-load", "provider-mock"}.intersection(configuration["services"])
    print(
        "Topology: no API/Redis host ports; isolated cache has only authorized app/Redis; no load/mock services."
    )
