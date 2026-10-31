import pytest

from climaprev.tools.spatial_comparison import paired_cases


def test_intersection_excludes_missing_and_non_original_dates():
    a = [{"date": day, "station": 1} for day in ("01", "02", "03")]
    b = [{"date": day, "station": 1} for day in ("02", "03", "04")]
    left, right = paired_cases(a, b, {"01", "02", "04"})
    assert left == right == [{"date": "02", "station": 1}]


def test_duplicate_or_different_station_target_rejected():
    row = {"date": "01", "station": 1}
    with pytest.raises(ValueError, match="duplicate"):
        paired_cases([row, row], [row], {"01"})
    with pytest.raises(ValueError, match="targets"):
        paired_cases([row], [{**row, "station": 2}], {"01"})
