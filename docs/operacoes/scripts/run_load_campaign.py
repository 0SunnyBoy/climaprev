"""Bounded sustained synthetic load; preserve raw CSVs and distinguish capacity from availability."""
import argparse
import csv
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

SCENARIOS = ("warm_cache", "cold_cache", "lock_contention", "slow_upstream", "redis_latency")
COMPOSE = ["docker", "compose", "-f", "docker-compose.yml", "-f", "docker/load-bounded.yml", "--profile", "load"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=90)
    parser.add_argument("--users", type=int, default=10)
    args = parser.parse_args()
    if not 30 <= args.seconds <= 300 or not 1 <= args.users <= 50:
        parser.error("local campaign is bounded to 30–300 seconds and 1–50 users")
    args.directory.mkdir(parents=True, exist_ok=False)
    results = []
    for scenario in SCENARIOS:
        env = {**os.environ, "CLIMAPREV_LOAD_SCENARIO": scenario}
        subprocess.run([*COMPOSE, "up", "-d", "--force-recreate", "--wait", "app-load", "provider-mock"],
                       env=env, check=True, capture_output=True)
        subprocess.run([*COMPOSE, "exec", "-T", "redis-load", "redis-cli", "FLUSHDB"],
                       env=env, check=True, capture_output=True)
        target = args.directory.resolve()
        command = [*COMPOSE, "run", "--rm", "--no-deps", "--volume", f"{target}:/results", "load",
                   "locust", "-f", "tests/load/locustfile.py", "--host", "http://app-load:8000",
                   "--headless", "--users", str(args.users), "--spawn-rate", str(args.users),
                   "--run-time", f"{args.seconds}s", "--only-summary", "--csv", f"/results/{scenario}"]
        run = subprocess.run(command, env=env, capture_output=True, text=True, check=False)
        (args.directory / f"{scenario}.log").write_text(run.stdout + run.stderr, encoding="utf-8")
        with (args.directory / f"{scenario}_stats.csv").open(encoding="utf-8") as source:
            row = next(row for row in csv.DictReader(source) if row["Name"] == "Aggregated")
        requests, failures = int(row["Request Count"]), int(row["Failure Count"])
        rate = float(row["Requests/s"])
        passed = run.returncode == 0 and requests > 0 and failures == 0 and args.users * 0.9 <= rate <= args.users * 1.1
        results.append({"scenario": scenario, "returncode": run.returncode, "requests": requests,
                        "failures": failures, "requests_per_second": rate,
                        "p50_ms": float(row["50%"]), "p95_ms": float(row["95%"]),
                        "p99_ms": float(row["99%"]), "arrival_target_met": args.users * 0.9 <= rate <= args.users * 1.1,
                        "passed_local_gate": passed})
        report = {"updated_utc": datetime.now(UTC).isoformat(), "users": args.users,
                  "seconds_per_scenario": args.seconds, "results": results,
                  "all_scenarios_finished": len(results) == len(SCENARIOS),
                  "production_capacity_approved": False,
                  "limitations": "Shared host with bounded containers, two API workers and mock provider; "
                                 "not dedicated infrastructure or real-provider availability validation."}
        (args.directory / "summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(results[-1]), flush=True)
    stats = subprocess.run(["docker", "stats", "--no-stream", "--format", "{{json .}}",
                            "climaprev-develop-app-load-1", "climaprev-develop-provider-mock-1",
                            "climaprev-develop-redis-load-1"],
                           capture_output=True, text=True, check=True)
    (args.directory / "resource-snapshot.jsonl").write_text(stats.stdout, encoding="utf-8")


if __name__ == "__main__":
    main()
