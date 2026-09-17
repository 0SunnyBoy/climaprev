"""Container readiness probe without shell-dependent command quoting."""
from urllib.request import urlopen


def main() -> None:
    with urlopen("http://localhost:8000/health/ready", timeout=2) as response:
        if response.status != 200:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
