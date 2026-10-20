"""Inventory local artifact metadata without reading reserved weather outcomes."""

import hashlib
import json
from pathlib import Path


def main():
    evidence = Path("docs/planejamento/reference-candidate-1/evidence")
    output = evidence / "inventario-reservas-2026-10-19-v2.json"
    if output.exists():
        raise ValueError("inventory already exists")
    old_path = evidence / "auditoria-periodos-locais.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    manifest_path = evidence / "coleta-espacial-2026-10-19.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    known = {row["file"].replace("\\", "/"): {
        "start": row["start"], "end": row["end"], "basis": "prior local period audit"}
        for row in old["entries"]}
    for name in manifest["parent_snapshots"]:
        known[f".historical-reports/spatial-2024-2026-10-19/{name}.inputs.json"] = {
            "start": f"2024-{name.split('-2024-')[1][:2]}-01",
            "end": f"2024-{name.split('-2024-')[1][:2]}-29",
            "basis": "completed spatial collection manifest"}
    found, unknown, tests = [], [], []
    for path in sorted(Path(".historical-reports").rglob("*.inputs.json")):
        name = path.as_posix()
        entry = {"path": name, "bytes": path.stat().st_size}
        if (path.parts[1].startswith("pytest-") and path.parent.name.startswith((
                "test_freeze_refuses_protocol_d", "test_preflight_then_resume_wit"))):
            entry["basis"] = "test output location and corresponding synthetic fixture code; content not inspected"
            tests.append(entry)
        elif name in known:
            entry.update(known[name])
            found.append(entry)
        else:
            unknown.append(entry)
    csvs = [{"path": path.as_posix(), "bytes": path.stat().st_size,
             "outcomes_read_by_this_audit": False}
            for path in sorted(Path(".historical-reports/inmet").glob("*.csv"))]
    reserved = [row for row in found if (
        row["start"] <= "2025-12-31" and row["end"] >= "2025-07-01") or (
        row["start"] <= "2026-06-30" and row["end"] >= "2026-01-01")]
    report = {
        "schema": "climaprev-reservation-metadata-inventory-v1",
        "scope": "current local snapshot filenames/sizes plus prior audit and collection metadata only",
        "known_snapshots": found, "unknown_snapshot_metadata": unknown,
        "test_artifact_metadata": tests,
        "missing_previously_known_snapshots": sorted(set(known) - {row["path"] for row in found}),
        "known_reserved_period_matches": reserved, "station_csv_metadata": csvs,
        "previous_structural_exposure": {
            "annual_2025_csv_obtained": True,
            "annual_csv_parser_processes_all_rows_before_period_filter": True,
            "distinction": "structural processing is documented; no proof of absent prior outcome review",
            "known_reviewed_pilot": "Belém January 2025; excluded from unseen validation/test"},
        "parents": {str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in (old_path, manifest_path)},
        "reserved_outcomes_inspected_by_this_audit": False,
        "unseen_status": "not_certified_requires_provenance_review",
        "external_access_history_audited": False,
        "candidate_fitting_executed": False, "stop_before_stage": 6,
        "limitations": ["Known dates are inherited metadata; raw snapshot outcomes were not reopened.",
                        "Current local absence does not prove no deleted, remote or previous access.",
                        "Unknown snapshots require metadata-only review before any unseen claim."]}
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(f"Known snapshots {len(found)}; unknown {len(unknown)}; reserved matches {len(reserved)}")


if __name__ == "__main__":
    main()
