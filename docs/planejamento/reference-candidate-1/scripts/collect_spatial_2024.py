"""Run the verified preparation plan; preserve each execution manifest."""

import argparse
import asyncio
import json
from pathlib import Path

from prepare_spatial_2024 import verified_plan

from climaprev.tools.collect_spatial import collect_spatial


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("execution manifest already exists")
    evidence = Path("docs/planejamento/reference-candidate-1/evidence")
    plan = json.loads((evidence / "plano-espacial-2024-2026-10-19.json").read_text(encoding="utf-8"))
    report = asyncio.run(collect_spatial(
        plan, verified_plan(), Path(".historical-reports/spatial-2024-2026-10-19"),
        preflight_only=args.preflight_only))
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    if report["failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
