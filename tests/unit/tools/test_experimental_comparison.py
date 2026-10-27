import json
import subprocess
import sys
from copy import deepcopy
from datetime import UTC, date, datetime, timedelta

import pytest

from climaprev.tools.experimental_comparison import compare_rain_models


def report(model, predictions, observations, *, run=True, late=False):
    collected = datetime(2024, 1, 2, tzinfo=UTC) if late else datetime(2023, 12, 31, tzinfo=UTC)
    rows = []
    for index, (predicted, observed) in enumerate(zip(predictions, observations, strict=True)):
        day = date(2024, 1, 1) + timedelta(days=index)
        start = datetime.combine(day, datetime.min.time(), UTC)
        rows.append({"date": day.isoformat(), "start_utc": start.isoformat(),
                     "end_utc": (start + timedelta(days=1)).isoformat(),
                     "forecast_mm": predicted, "observed_mm": observed,
                     "exclusions": [], "eligible_exploratory": True,
                     "collection_lead_days": (day - collected.date()).days})
    return {"schema": "climaprev-station-rain-pairs-v2", "model": model,
            "station": {"code": "synthetic-station", "latitude": 0, "longitude": 0},
            "location": {"latitude": 0, "longitude": 0, "timezone": "UTC"},
            "source_sha256": "synthetic-common-source", "collected_at": collected.isoformat(),
            "run_at": (collected - timedelta(hours=6)).isoformat() if run else None,
            "rows": rows}


def test_known_errors_are_paired_and_stratified_without_promoting():
    baseline = report("baseline", [10, 70], [0, 50])
    candidate = report("candidate", [5, 60], [0, 50])
    result = compare_rain_models([baseline, candidate], "baseline")
    assert result["common_cases"] == 2
    score = result["models"]["baseline"]["numerical"]
    assert score["mae"] == 15
    assert score["bias"] == 15
    assert score["rmse"] == pytest.approx(250 ** 0.5)
    assert result["models"]["candidate"]["relative_mae_gain"] == 0.5
    assert len(result["strata"]) == 2
    assert not result["scientific_approval"]
    assert not result["promotion_allowed"]


def test_coverage_and_absent_rows_are_visible_on_the_common_sample():
    baseline = report("baseline", [10, 70, 2], [0, 50, 0])
    candidate = report("candidate", [None, 60, 2], [0, 50, 0])
    candidate["rows"].pop()
    result = compare_rain_models([baseline, candidate], "baseline")
    assert result["common_cases"] == 1
    assert result["reported_union_cases"] == 3
    assert result["models"]["candidate"]["excluded_unique_cases"] == 1
    assert result["models"]["candidate"]["absent_from_reported_union"] == 1
    assert result["models"]["baseline"]["eligible_outside_common"] == 2
    assert result["models"]["baseline"]["numerical"]["mae"] == 20


@pytest.mark.parametrize("late,run,reason", [
    (True, True, "collected_not_before_target"),
    (False, False, "run_unknown_or_not_before_target"),
])
def test_timing_is_recomputed_not_trusted_from_eligibility_labels(late, run, reason):
    arms = [report(model, [1], [1], late=late, run=run) for model in ("baseline", "candidate")]
    result = compare_rain_models(arms, "baseline")
    assert result["common_cases"] == 0
    assert result["models"]["candidate"]["excluded_reasons"][reason] == 1
    assert result["models"]["candidate"]["numerical"]["mae"] is None


def test_retrospective_mode_requires_explicit_opt_in_and_remains_exploratory():
    arms = [report(model, [1], [1], late=True, run=False) for model in ("baseline", "candidate")]
    result = compare_rain_models(arms, "baseline", allow_retrospective=True, require_run=False)
    assert result["common_cases"] == 1
    assert result["timing_mode"] == "retrospective_allowed"
    assert not result["promotion_allowed"]


def test_no_observed_extremes_and_zero_baseline_error_do_not_become_perfect_skill():
    result = compare_rain_models([report(m, [0], [0]) for m in ("b", "c")], "b")
    assert result["models"]["c"]["relative_mae_gain"] is None
    assert result["models"]["c"]["high_rain_detection"]["recall"] is None
    assert result["models"]["c"]["high_rain_detection"]["false_alarm_ratio"] is None


def test_empty_reports_keep_metrics_undefined():
    result = compare_rain_models([report(m, [], []) for m in ("b", "c")], "b")
    assert result["common_cases"] == 0
    assert result["reported_union_cases"] == 0
    assert result["models"]["b"]["numerical"]["mae"] is None


def test_d7_without_baseline_stays_visible_but_has_no_paired_score():
    baseline = report("baseline", [1], [1])
    candidate = report("candidate", [1, 2], [1, 2])
    row = candidate["rows"][1]
    row.update(date="2024-01-07", start_utc="2024-01-07T00:00:00+00:00",
               end_utc="2024-01-08T00:00:00+00:00", collection_lead_days=7)
    result = compare_rain_models([baseline, candidate], "baseline")
    d7 = next(s for s in result["strata"] if s["collection_lead_days"] == 7)
    assert d7["common_cases"] == 0
    assert d7["models"]["baseline"]["absent_from_reported_union"] == 1
    assert d7["models"]["candidate"]["numerical"]["mae"] is None


def test_reports_hits_misses_and_false_alarms():
    baseline = report("baseline", [50, 0, 0, 0], [50, 50, 0, 0])
    candidate = report("candidate", [50, 0, 50, 0], [50, 50, 0, 0])
    score = compare_rain_models([baseline, candidate], "baseline")["models"]["candidate"]
    assert score["high_rain_detection"]["hits"] == 1
    assert score["high_rain_detection"]["misses"] == 1
    assert score["high_rain_detection"]["false_alarms"] == 1
    assert score["high_rain_detection"]["recall"] == 0.5
    assert score["high_rain_detection"]["false_alarm_ratio"] == 0.5


@pytest.mark.parametrize("invalid", ["duplicate", "observation", "source", "negative", "nan", "lead", "day", "point"])
def test_rejects_noncomparable_or_malformed_cases(invalid):
    baseline = report("b", [1], [1])
    candidate = deepcopy(report("c", [1], [1]))
    if invalid == "duplicate":
        candidate["rows"].append(deepcopy(candidate["rows"][0]))
    elif invalid == "observation":
        candidate["rows"][0]["observed_mm"] = 2
    elif invalid == "source":
        candidate["source_sha256"] = "other-source"
    elif invalid == "negative":
        candidate["rows"][0]["forecast_mm"] = -0.1
    elif invalid == "nan":
        candidate["rows"][0]["forecast_mm"] = float("nan")
    elif invalid == "lead":
        candidate["rows"][0]["collection_lead_days"] = 7
    elif invalid == "day":
        candidate["rows"][0]["date"] = "2024-01-02"
    else:
        candidate["location"]["latitude"] = 1
    with pytest.raises(ValueError):
        compare_rain_models([baseline, candidate], "b")


def test_cli_compares_explicit_files_and_never_overwrites_result(tmp_path):
    inputs = []
    for model in ("baseline", "candidate"):
        path = tmp_path / f"{model}.json"
        path.write_text(json.dumps(report(model, [1], [1])))
        inputs.extend(["--input", str(path)])
    output = tmp_path / "result.json"
    command = [sys.executable, "-m", "climaprev.tools.experimental_comparison", *inputs,
               "--baseline", "baseline", "--output", str(output)]
    subprocess.run(command, check=True, capture_output=True)
    before = output.read_bytes()
    assert json.loads(before)["common_cases"] == 1
    repeat = subprocess.run(command, check=False, capture_output=True)
    assert repeat.returncode == 2
    assert output.read_bytes() == before
