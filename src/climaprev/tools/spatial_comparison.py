"""Descriptive spatial comparisons on identical station days; no inference or fit."""

from dataclasses import asdict
from typing import Any

from climaprev.domain.verification import numerical_pairs
from climaprev.tools.station_baseline import baseline_event


def paired_cases(
    control: list[dict[str, Any]], station: list[dict[str, Any]], eligible: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    indexes = []
    for rows in (control, station):
        index = {row["date"]: row for row in rows}
        if len(index) != len(rows):
            raise ValueError("duplicate spatial comparison date")
        indexes.append(index)
    dates = sorted(eligible & indexes[0].keys() & indexes[1].keys())
    for day in dates:
        if indexes[0][day]["station"] != indexes[1][day]["station"]:
            raise ValueError("spatial arms have different station targets")
    return ([indexes[0][day] for day in dates], [indexes[1][day] for day in dates])


def summarize(event: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    return {"classification": baseline_event(event, cases),
            "numerical": {source: asdict(numerical_pairs([
                (row["station"], row[source]) for row in cases]))
                for source in ("forecast", "observed")}}
