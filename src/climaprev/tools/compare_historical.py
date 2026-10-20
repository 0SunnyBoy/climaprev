"""Compare saved historical cases using fixed observed labels; no network or promotion."""

import argparse
import json
from pathlib import Path

from climaprev.application.errors import WeatherDataInvalid
from climaprev.tools.historical_experiment import (
    evaluate_snapshots,
    load_calibration,
    load_candidate,
    load_snapshot,
    read_json,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, nargs="+", required=True)
    parser.add_argument("--candidate", type=Path)
    parser.add_argument("--calibration", type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--partition", choices=("diagnostic", "adjustment", "validation", "test"),
                        default="diagnostic")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        report = evaluate_snapshots(
            [load_snapshot(path) for path in args.input],
            candidate=load_candidate(args.candidate) if args.candidate else None,
            calibration=load_calibration(args.calibration) if args.calibration else None,
            protocol=read_json(args.protocol) if args.protocol else None, partition=args.partition,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
                               + "\n", encoding="utf-8")
        print(f"Diagnostic comparison written to {args.output}; no configuration approved")
    except (ValueError, WeatherDataInvalid, OSError, TypeError, KeyError) as error:
        parser.exit(2, f"historical comparison failed: {error}\n")


if __name__ == "__main__":
    main()
