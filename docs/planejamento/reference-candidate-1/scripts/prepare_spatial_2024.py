"""Freeze the spatial request plan from verified local INMET annual files."""

import json
from pathlib import Path

from climaprev.tools.spatial_plan import STATIONS, spatial_plan


def verified_plan():
    root = Path(__file__).resolve().parents[4]
    evidence = root / "docs/planejamento/reference-candidate-1/evidence"
    protocol = json.loads((root / "docs/planejamento/reference-candidate-1/protocolo-etapas-1-a-5.json")
                          .read_text(encoding="utf-8"))
    sources = {}
    for city, code in STATIONS.items():
        acquisition = json.loads((evidence / f"obtencao-inmet-{code.lower()}-2024-2026-10-19.json")
                                 .read_text(encoding="utf-8"))
        sources[city] = ((root / f".historical-reports/inmet/{code}-2024.csv").read_bytes(),
                         acquisition["csv_sha256"])
    return spatial_plan(protocol, sources)


def main() -> None:
    root = Path(__file__).resolve().parents[4]
    evidence = root / "docs/planejamento/reference-candidate-1/evidence"
    plan = verified_plan()
    target = evidence / "plano-espacial-2024-2026-10-19.json"
    encoded = json.dumps(plan, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    if target.exists():
        if target.read_text(encoding="utf-8") != encoded:
            raise ValueError("frozen spatial plan differs; use a new version")
    else:
        with target.open("x", encoding="utf-8") as output:
            output.write(encoded)
    print(f"Verified plan: {plan['snapshot_count']} snapshots; collection not executed")


if __name__ == "__main__":
    main()
