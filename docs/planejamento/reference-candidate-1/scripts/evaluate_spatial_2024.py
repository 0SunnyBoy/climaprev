"""Compare both spatial arms on common days, preserving all source snapshots."""

import hashlib
import json
from collections import defaultdict
from copy import deepcopy
from pathlib import Path

from climaprev.tools.compare_hourly_rain import compare_hourly_rain
from climaprev.tools.compare_station import compare_station
from climaprev.tools.compare_station_variables import compare_variables
from climaprev.tools.historical_experiment import digest, load_snapshot
from climaprev.tools.spatial_comparison import paired_cases, summarize


def main():
    evidence = Path("docs/planejamento/reference-candidate-1/evidence")
    plan = json.loads((evidence / "plano-espacial-2024-2026-10-19.json").read_text(encoding="utf-8"))
    manifest = json.loads((evidence / "coleta-espacial-2026-10-19.json").read_text(encoding="utf-8"))
    summary_bytes = (evidence / "sintese-observacional-2024-2026-10-19.json").read_bytes()
    summary = json.loads(summary_bytes)
    parent = json.loads((evidence / "baseline-observacional-2024-final-2026-10-19.json")
                        .read_text(encoding="utf-8"))
    if hashlib.sha256(summary_bytes).hexdigest() != parent["summary_sha256"]:
        raise ValueError("original eligibility summary changed")
    if not manifest["complete"] or manifest["plan_sha256"] != digest(plan):
        raise ValueError("complete verified collection required")
    output = evidence / "comparacao-espacial-2024-2026-10-19.json"
    if output.exists():
        raise ValueError("comparison already exists")
    pooled = defaultdict(list)
    strata = []
    grids = []
    event_fields = {"daily_rain": "rain_mm", "hourly_rain": "rain_mm", "gust": "gust_kmh",
                    "heat": "temperature_max_c", "cold": "temperature_min_c"}
    for group in summary["groups"]:
        city, month = group["location"], group["month"]
        station = plan["stations"][city]
        raw = Path(f".historical-reports/inmet/{station['code']}-2024.csv").read_bytes()
        if hashlib.sha256(raw).hexdigest() != station["csv_sha256"]:
            raise ValueError("station CSV changed")
        for lead in (1, 3, 7):
            pair = f"{city}-2024-{month:02d}-d{lead}"
            arms = {}
            for arm in ("municipal-control", "station"):
                name = f"{pair}-{arm}"
                data = load_snapshot(Path(f".historical-reports/spatial-2024-2026-10-19/{name}.inputs.json"))
                if digest(data) != manifest["parent_snapshots"][name]:
                    raise ValueError("spatial snapshot changed")
                grids.append({"pair": pair, "arm": arm,
                              "sources": {source: {key: data[source][key] for key in
                                                   ("latitude", "longitude", "elevation")}
                                          for source in ("forecast", "observed")}})
                data = deepcopy(data)
                data["configuration"]["end"] = f"2024-{month:02d}-28"
                kwargs = {"expected_station": station["code"]}
                variables = compare_variables(data, raw, **kwargs)["variables"]
                arms[arm] = {
                    "daily_rain": compare_station(data, raw, **kwargs)["cases"],
                    "hourly_rain": compare_hourly_rain(data, raw, **kwargs)["cases"],
                    **{event: variables[field]["cases"] for event, field in event_fields.items()
                       if event in ("gust", "heat", "cold")}}
            for event, field in event_fields.items():
                eligible = set(group["variables"][field]["common_dates"])
                left, right = paired_cases(arms["municipal-control"][event], arms["station"][event], eligible)
                result = {"pair": pair, "event": event, "original_eligible": len(eligible),
                          "paired_dates": [row["date"] for row in left],
                          "excluded_original_dates": sorted(eligible - {row["date"] for row in left})}
                for arm, rows in (("municipal-control", left), ("station", right)):
                    rows = [{**row, "location": city} for row in rows]
                    result[arm] = summarize(event, rows)
                    pooled[event, lead, arm].extend(rows)
                strata.append(result)
    report = {
        "schema": "climaprev-spatial-comparison-v1", "plan_sha256": digest(plan),
        "collection_sha256": digest(manifest), "summary_file_sha256": hashlib.sha256(summary_bytes).hexdigest(),
        "strata": strata, "returned_grids": grids,
        "source_sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in (
            Path(__file__), Path("src/climaprev/tools/spatial_comparison.py"),
            Path("src/climaprev/tools/compare_station.py"),
            Path("src/climaprev/tools/compare_hourly_rain.py"),
            Path("src/climaprev/tools/compare_station_variables.py"),
            Path("src/climaprev/tools/inmet_observations.py"),
            Path("src/climaprev/tools/audit_historical.py"),
            Path("src/climaprev/tools/station_baseline.py"))},
        "aggregates": [{"event": event, "lead_days": lead, "arm": arm, **summarize(event, rows)}
                       for (event, lead, arm), rows in sorted(pooled.items())],
        "scientific_approval": False, "candidate_fitting_executed": False,
        "calibration_fitting_executed": False, "stop_before_stage": 6,
        "limitations": ["Descriptive comparison only; no approved confidence intervals or causal claim.",
                        "Same days within each pair/horizon; horizons are not independent replications.",
                        "Thermal samples and gust semantics retain earlier limitations.",
                        "Grid centers can coincide despite different requested coordinates."]}
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(f"Compared {len(strata)} strata")


if __name__ == "__main__":
    main()
