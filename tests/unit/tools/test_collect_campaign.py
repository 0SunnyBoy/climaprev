from copy import deepcopy
from datetime import date

import pytest

from climaprev.application.errors import ProviderTransientError
from climaprev.tools.collect_campaign import campaign_jobs, diagnostic_window, run_campaign


def protocol():
    return {
        "authorization": {"allowed_stages": [1, 2, 3, 4, 5],
                          "candidate_fitting_allowed": False, "calibration_fitting_allowed": False},
        "splits": {"adjustment": {"start": "2024-01-01", "end": "2024-12-31"}},
        "initial_adjustment_collection": {
            "locations": ["Belém", "Brasília", "Porto Alegre"], "year": 2024,
            "months": [1, 4, 7, 10], "lead_days": [1, 3, 7],
            "days_in_each_month": {"first": 1, "last": 28, "boundary_day": 29}},
    }


def test_fixed_campaign_stays_inside_adjustment_and_never_opens_holdout():
    jobs = campaign_jobs(protocol())
    assert len(jobs) == 36
    assert {config.lead_days for _, config in jobs} == {1, 3, 7}
    assert all(date(2024, 1, 1) <= config.start < config.end <= date(2024, 12, 31)
               for _, config in jobs)


@pytest.mark.parametrize("change", ["fitting", "outside", "boundary", "duplicate"])
def test_invalid_campaign_cannot_access_other_partitions(change):
    plan = protocol()
    if change == "fitting":
        plan["authorization"]["candidate_fitting_allowed"] = True
    elif change == "outside":
        plan["initial_adjustment_collection"]["year"] = 2025
    elif change == "boundary":
        plan["initial_adjustment_collection"]["days_in_each_month"]["boundary_day"] = 30
    else:
        plan["initial_adjustment_collection"]["lead_days"] = [1, 1]
    with pytest.raises(ValueError):
        campaign_jobs(plan)


def test_boundary_day_is_not_counted_as_an_extra_evaluation_day():
    original = {"configuration": {"end": "2024-01-29"}, "raw": [1, 2, 3]}
    before = deepcopy(original)
    derived = diagnostic_window(original)
    assert derived["configuration"]["end"] == "2024-01-28"
    assert original == before
    assert derived["campaign_parent_sha256"]


@pytest.mark.asyncio
async def test_transient_failure_is_reported_without_fabricating_observations(tmp_path, monkeypatch):
    plan = protocol()
    plan["initial_adjustment_collection"]["months"] = [1]
    plan["initial_adjustment_collection"]["lead_days"] = [1]

    async def failing(config, *, save_input):
        raise ProviderTransientError("provider temporarily unavailable")

    monkeypatch.setattr("climaprev.tools.collect_campaign.collect_and_validate", failing)
    result = await run_campaign(plan, tmp_path)
    assert result["collected_jobs"] == 0
    assert len(result["failures"]) == 3
    assert result["unique_location_dates"] == 0
    assert not result["candidate_fitting_executed"]
    assert not result["holdout_accessed_by_campaign"]


def test_freeze_refuses_protocol_drift_and_does_not_authorize_fitting(tmp_path, monkeypatch):
    from climaprev.tools.freeze_preparation import freeze
    from climaprev.tools.historical_experiment import digest

    plan = protocol()
    plan["authorization"]["first_forbidden_stage"] = 6
    plan["scientific_approval"] = None
    data = {"configuration": {"start": "2024-04-01", "end": "2024-04-29"},
            "reference": {"policy_sha256": "fixed-policy"}}
    (tmp_path / "sample.inputs.json").write_text("immutable fixture", encoding="utf-8")
    monkeypatch.setattr("climaprev.tools.freeze_preparation.load_snapshot", lambda path: data)
    campaign = {"protocol_sha256": digest(plan), "parent_snapshots": {"sample": digest(data)}}
    result = freeze(plan, campaign, tmp_path)
    assert result["reference_policy_sha256"] == "fixed-policy"
    assert not result["stage_6_authorized"]
    assert result["scientific_approval"] is None
    plan["scientific_approval"] = "unexpected edit"
    with pytest.raises(ValueError, match="protocol"):
        freeze(plan, campaign, tmp_path)


def test_freeze_rejects_changed_parent(tmp_path, monkeypatch):
    from climaprev.tools.freeze_preparation import freeze
    from climaprev.tools.historical_experiment import digest

    plan = protocol()
    plan["authorization"]["first_forbidden_stage"] = 6
    monkeypatch.setattr("climaprev.tools.freeze_preparation.load_snapshot", lambda path: {})
    campaign = {"protocol_sha256": digest(plan), "parent_snapshots": {"sample": "changed"}}
    with pytest.raises(ValueError, match="parent changed"):
        freeze(plan, campaign, tmp_path)
