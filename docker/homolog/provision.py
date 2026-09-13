"""Provision only local generated credentials; never print their contents."""
import argparse
import hashlib
import secrets
from pathlib import Path


def provision(directory: Path, capacity: int, refill: int, window: int) -> None:
    if min(capacity, refill, window) <= 0:
        raise ValueError("budgets must be positive")
    directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    password = secrets.token_urlsafe(32)
    secret = directory / "redis.password"
    secret.write_text(password)
    secret.chmod(0o444)
    digest = hashlib.sha256(password.encode()).hexdigest()
    acl = directory / "redis.acl"
    acl.write_text("user default off\nuser climaprev on #" + digest +
                   " ~climaprev:* +ping +select +get +set +del +eval +hmget +hset"
                   " +pexpire +expire +exists +pttl +ttl +scan +hgetall +client|setinfo\n")
    acl.chmod(0o444)
    (directory / "compose.env").write_text(
        f"CLIMAPREV_HOMOLOG_DIR={directory.resolve()}\n"
        f"CLIMAPREV_PROVIDER_BUDGET_CAPACITY={capacity}\n"
        f"CLIMAPREV_PROVIDER_BUDGET_REFILL={refill}\n"
        f"CLIMAPREV_PROVIDER_BUDGET_WINDOW_SECONDS={window}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--capacity", type=int, required=True)
    parser.add_argument("--refill", type=int, required=True)
    parser.add_argument("--window", type=int, default=60)
    args = parser.parse_args()
    provision(args.directory, args.capacity, args.refill, args.window)
    print("Local configuration provisioned; credentials are not displayed.")
