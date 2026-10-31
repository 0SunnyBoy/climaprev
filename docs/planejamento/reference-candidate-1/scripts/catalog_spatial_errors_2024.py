"""Reconstruct paired cases and reconcile the immutable spatial comparison."""

import hashlib
import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

from climaprev.tools.compare_hourly_rain import compare_hourly_rain
from climaprev.tools.compare_station import compare_station
from climaprev.tools.compare_station_variables import compare_variables
from climaprev.tools.error_catalog import catalog_pair
from climaprev.tools.historical_experiment import digest, load_snapshot
from climaprev.tools.spatial_comparison import paired_cases, summarize


def main():
    evidence = Path("docs/planejamento/reference-candidate-1/evidence")
    output = evidence / "catalogo-erros-espaciais-2024-2026-10-19.json"
    if output.exists():
        raise ValueError("catalog already exists")
    files = {name: evidence / filename for name, filename in {
        "comparison": "comparacao-espacial-2024-2026-10-19.json",
        "plan": "plano-espacial-2024-2026-10-19.json",
        "manifest": "coleta-espacial-2026-10-19.json",
        "summary": "sintese-observacional-2024-2026-10-19.json"}.items()}
    documents = {key: json.loads(path.read_text(encoding="utf-8")) for key, path in files.items()}
    comparison, plan, manifest, summary = (documents[key] for key in files)
    if (comparison["plan_sha256"] != digest(plan)
            or comparison["collection_sha256"] != digest(manifest)
            or comparison["summary_file_sha256"] != hashlib.sha256(files["summary"].read_bytes()).hexdigest()
            or not manifest["complete"] or manifest["failures"]):
        raise ValueError("comparison provenance differs")
    for filename, checksum in comparison["source_sha256"].items():
        if hashlib.sha256(Path(filename).read_bytes()).hexdigest() != checksum:
            raise ValueError("comparison source changed")
    expected = {f"{job['pair']}-{job['arm']}": job for job in plan["requests"]}
    if len(expected) != 72 or set(expected) != set(manifest["parent_snapshots"]):
        raise ValueError("spatial snapshot set differs")
    reference = {(row["pair"], row["event"]): row for row in comparison["strata"]}
    if len(reference) != 180 or len(comparison["strata"]) != 180:
        raise ValueError("spatial strata set differs")
    fields = {"daily_rain": "rain_mm", "hourly_rain": "rain_mm", "gust": "gust_kmh",
              "heat": "temperature_max_c", "cold": "temperature_min_c"}
    cases, reconciled = [], []
    for group in summary["groups"]:
        city, month = group["location"], group["month"]
        station = plan["stations"][city]
        raw = Path(f".historical-reports/inmet/{station['code']}-2024.csv").read_bytes()
        if hashlib.sha256(raw).hexdigest() != station["csv_sha256"]:
            raise ValueError("CSV changed")
        for lead in (1, 3, 7):
            pair = f"{city}-2024-{month:02d}-d{lead}"
            arms, parents = {}, {}
            for arm in ("municipal-control", "station"):
                name = f"{pair}-{arm}"
                data = load_snapshot(Path(f".historical-reports/spatial-2024-2026-10-19/{name}.inputs.json"))
                parents[arm] = digest(data)
                if parents[arm] != manifest["parent_snapshots"][name]:
                    raise ValueError("snapshot changed")
                if data["configuration"]["spatial_plan_sha256"] != digest(plan):
                    raise ValueError("snapshot plan differs")
                for source in ("forecast", "observed"):
                    if data["requests"][source]["params"] != expected[name]["parameters"][source]:
                        raise ValueError("snapshot parameters differ")
                data = deepcopy(data)
                data["configuration"]["end"] = f"2024-{month:02d}-28"
                kwargs = {"expected_station": station["code"]}
                variables = compare_variables(data, raw, **kwargs)["variables"]
                arms[arm] = {
                    "daily_rain": compare_station(data, raw, **kwargs)["cases"],
                    "hourly_rain": compare_hourly_rain(data, raw, **kwargs)["cases"],
                    **{event: variables[field]["cases"] for event, field in fields.items()
                       if event in ("gust", "heat", "cold")}}
            for event, field in fields.items():
                eligible = set(group["variables"][field]["common_dates"])
                left, right = paired_cases(arms["municipal-control"][event], arms["station"][event], eligible)
                original = reference[pair, event]
                if [row["date"] for row in left] != original["paired_dates"]:
                    raise ValueError("paired dates differ")
                for arm, rows in (("municipal-control", left), ("station", right)):
                    if digest(summarize(event, [{**row, "location": city} for row in rows])) != digest(original[arm]):
                        raise ValueError("reconstructed metrics differ")
                reconciled.append({"pair": pair, "event": event})
                for row in catalog_pair(event, left, right, eligible):
                    cases.append({"location": city, "station": station["code"], "event": event,
                                  "lead_days": lead, "parent_snapshots": parents,
                                  "station_csv_sha256": station["csv_sha256"], **row})
    high = [row for row in cases if row["high_relevant"]]
    observed_high_units = sorted({(row["location"], row["date"]) for row in cases
                                  if row["station_level"] == "high"})
    report = {
        "schema": "climaprev-spatial-error-catalog-v1", "cases": cases,
        "high_relevant_cases": high, "observed_high_location_dates": observed_high_units,
        "reconciled_strata": reconciled,
        "case_counts_by_event": dict(Counter(row["event"] for row in cases)),
        "parents": {key: {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                    for key, path in files.items()},
        "source_sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in (
            Path(__file__), Path("src/climaprev/tools/error_catalog.py"))},
        "scientific_approval": False, "candidate_fitting_executed": False,
        "calibration_fitting_executed": False, "stop_before_stage": 6,
        "limitations": ["Repeated horizons and arms are not independent observations.",
                        "Misses and false alarms describe thresholds on aggregates, not disaster impacts.",
                        "Causes remain unproven; moderate-event tradeoffs must also be reviewed."]}
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(f"Reconciled {len(reconciled)} strata, {len(cases)} cases, {len(high)} high-relevant cases")


if __name__ == "__main__":
    main()
