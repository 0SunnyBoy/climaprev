"""Freeze preparation evidence and explicitly retain the stop before stage 6."""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from climaprev.tools.historical_experiment import digest, load_snapshot


def freeze(protocol: dict[str, Any], campaign: dict[str, Any], directory: Path) -> dict[str, Any]:
    if campaign["protocol_sha256"] != digest(protocol):
        raise ValueError("campaign does not match the frozen protocol")
    authorization = protocol["authorization"]
    if (authorization["first_forbidden_stage"] != 6
            or authorization["candidate_fitting_allowed"]
            or authorization["calibration_fitting_allowed"]):
        raise ValueError("this freeze is restricted to preparation before stage 6")
    parents = {}
    policies = set()
    for name, expected in campaign["parent_snapshots"].items():
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("invalid campaign snapshot identifier")
        path = directory / f"{name}.inputs.json"
        dataset = load_snapshot(path)
        if digest(dataset) != expected:
            raise ValueError(f"campaign parent changed: {name}")
        config = dataset["configuration"]
        split = protocol["splits"]["adjustment"]
        if not split["start"] <= config["start"] <= config["end"] <= split["end"]:
            raise ValueError("preparation input is outside adjustment")
        policies.add(dataset["reference"]["policy_sha256"])
        parents[name] = {"dataset_sha256": expected,
                         "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "start": config["start"], "end": config["end"]}
    if len(policies) != 1:
        raise ValueError("preparation must have one frozen reference policy")
    source_root = Path(__file__).resolve().parents[1]
    return {
        "schema": "climaprev-preparation-freeze-v1", "protocol_sha256": digest(protocol),
        "campaign_sha256": digest(campaign), "parent_snapshots": parents,
        "reference_policy_sha256": next(iter(policies)),
        "source_files_sha256": {str(path.relative_to(source_root)).replace("\\", "/"):
                                hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in sorted(source_root.rglob("*.py"))},
        "scientific_approval": protocol["scientific_approval"],
        "stage_6_authorized": False, "candidate_or_calibration_fitted": False,
        "readiness": "technical_preparation_frozen_external_validation_pending",
        "outstanding_gates": [
            "Official station CSV compatibility, identity and sensor quality remain unvalidated.",
            "Real station comparisons remain unexecuted.",
            "Primary event/metric, event sufficiency and scientific minimum gain are unresolved.",
            "Temperature and gust sampling differences require scientific review.",
            "User explicitly required stopping before stage 6.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = freeze(json.loads(args.protocol.read_text(encoding="utf-8")),
                    json.loads(args.campaign.read_text(encoding="utf-8")), args.directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        output.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
