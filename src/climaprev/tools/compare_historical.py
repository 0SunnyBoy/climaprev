"""Compare saved historical cases using fixed observed labels; no network or promotion."""

import argparse
import json
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from climaprev.application.errors import WeatherDataInvalid
from climaprev.domain.risk_policy import ExperimentalRiskPolicy
from climaprev.tools.experimental_candidate import _components, validate_candidate
from climaprev.tools.experimental_protocol import execute_authorized
from climaprev.tools.historical_experiment import (
    digest,
    evaluate_snapshots,
    load_calibration,
    load_candidate,
    load_snapshot,
    read_json,
)


def configuration_fingerprint(candidate: dict[str, Any]) -> str:
    value = validate_candidate(candidate)
    return digest({key: value[key] for key in ("policy", "calibration", "normalization", "models")})


def select_development(
    protocol: dict[str, Any], candidates: Sequence[dict[str, Any]], *,
    loaders: Mapping[str, Callable[[], Sequence[dict[str, Any]]]], mode: str = "development",
    approvals: Sequence[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Compare a finite predeclared space; the independent-test loader is never called."""
    if mode not in {"development", "diagnostic"}:
        raise ValueError("selection requires development or explicit synthetic diagnostic mode")

    def select(frozen: dict[str, Any]) -> dict[str, Any]:
        rule = frozen["criteria"].get("development", {})
        if (set(rule) != {"configurations", "event", "metric", "direction", "tie_break"}
                or rule["metric"] != "mae" or rule["direction"] != "min"
                or rule["tie_break"] != "configuration_sha256_ascending"):
            raise ValueError("development objective and tie rule must be predeclared")
        identities = [configuration_fingerprint(c) for c in candidates]
        if (not identities or len(set(identities)) != len(identities)
                or set(identities) != set(rule["configurations"])
                or any(c["candidate"]["protocol_sha256"] != protocol["sha256"] for c in candidates)):
            raise ValueError("configuration space differs from the declared protocol")
        if not {"adjustment", "validation"} <= set(loaders):
            raise ValueError("adjustment and validation loaders are required")
        datasets = {name: list(loaders[name]()) for name in ("adjustment", "validation")}
        scores = []
        for candidate, identity in sorted(zip(candidates, identities, strict=True), key=lambda c: c[1]):
            value = validate_candidate(candidate)
            policy, calibration = _components(value["policy"], value["calibration"])
            experimental = policy if isinstance(policy, ExperimentalRiskPolicy) else None
            profile = calibration if calibration.enabled else None
            variant = "AB" if experimental and profile else "A" if experimental else "B" if profile else "R0"
            reports = {name: evaluate_snapshots(data, candidate=experimental, calibration=profile,
                                               protocol=frozen, partition=name)
                       for name, data in datasets.items()}
            metrics = {}
            for name, report in reports.items():
                event = report["variants"][variant]["events"].get(rule["event"])
                if event is None or event["numerical"]["mae"] is None:
                    raise ValueError("development objective lacks eligible support")
                metrics[name] = event["numerical"]["mae"]
            scores.append({"candidate_sha256": candidate["sha256"], "configuration_sha256": identity,
                           "adjustment_score": metrics["adjustment"], "validation_score": metrics["validation"],
                           "reports": reports})
        selected = min(scores, key=lambda s: (s["validation_score"], s["configuration_sha256"]))
        return {"schema": "climaprev-development-selection-v1", "protocol_sha256": protocol["sha256"],
                "selected_candidate_sha256": selected["candidate_sha256"], "scores": scores,
                "rule": rule, "test_accesses": 0, "mode": mode, "promotion_allowed": False}

    return execute_authorized(protocol, mode, select, approvals=approvals)


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
