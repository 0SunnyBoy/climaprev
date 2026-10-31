import csv
import io
from datetime import UTC, datetime

import pytest

from climaprev.tools.inmet_observations import parse_station_csv
from climaprev.tools.inmet_tempo_csv import convert_tempo_csv

STATION = {"CD_ESTACAO": "A201", "DC_NOME": "Synthetic", "VL_LATITUDE": "0",
           "VL_LONGITUDE": "0", "VL_ALTITUDE": "10"}
NOW = datetime(2026, 10, 30, 12, tzinfo=UTC)
HEAD = ["Data", "Hora (UTC)", "Chuva (mm)", "Raj. Vento (m/s)",
        "Temp. Max. (C)", "Temp. Min. (C)", "Umi. Ins. (%)"]


def raw(rows=None, header=None):
    text = io.StringIO()
    writer = csv.writer(text, delimiter=";")
    writer.writerow(header or HEAD)
    writer.writerows(rows or [["29/10/2026", "0100", "1,5", "2", "25", "20", "50"]])
    return text.getvalue().encode()


def convert(payload, **overrides):
    options = {"station": STATION, "source_url": "https://tempo.inmet.gov.br/TabelaEstacoes/A201",
               "displayed_station": "Estação: Synthetic A201", "retrieved_at": NOW}
    options.update(overrides)
    return convert_tempo_csv(payload, **options)


def test_explicit_adapter_preserves_values_units_and_identity_provenance():
    source = raw()
    result = convert(source)
    metadata, hours = parse_station_csv(result.csv, expected_station="A201")
    assert metadata["code"] == "A201"
    assert hours[0].rain_mm == 1.5
    assert hours[0].gust_kmh == 7.2
    assert result.provenance["rows_imported"] == 1
    assert result.provenance["source_sha256"] != result.provenance["normalized_sha256"]
    assert not result.provenance["temperature_instant_imported"]
    assert not result.provenance["promotion_allowed"]
    assert b"BULBO SECO" not in result.csv


def test_only_entirely_blank_future_rows_can_be_omitted():
    rows = [["29/10/2026", "0100", "", "-9999", "25", "20", ""],
            ["31/10/2026", "0100", "", "", "", "", ""]]
    result = convert(raw(rows))
    assert result.provenance["blank_future_rows_omitted"] == 1
    assert parse_station_csv(result.csv, expected_station="A201")[1][0].rain_mm is None
    rows[1][2] = "0"
    with pytest.raises(ValueError, match="future"):
        convert(raw(rows))


@pytest.mark.parametrize("overrides", [
    {"source_url": "https://example.com/A201"},
    {"displayed_station": "Estação: Synthetic A001"},
    {"retrieved_at": NOW.replace(tzinfo=None)},
])
def test_invalid_binding_or_clock_rejected(overrides):
    with pytest.raises(ValueError):
        convert(raw(), **overrides)


@pytest.mark.parametrize("value", ["-1", "nan"])
def test_invalid_rain_rejected_by_unchanged_annual_importer(value):
    with pytest.raises(ValueError):
        convert(raw([["29/10/2026", "0100", value, "2", "25", "20", "50"]]))


def test_duplicate_hours_wrong_units_and_humidity_fail_closed():
    row = ["29/10/2026", "0100", "1", "2", "25", "20", "101"]
    with pytest.raises(ValueError, match="humidity"):
        convert(raw([row]))
    row[-1] = "50"
    with pytest.raises(ValueError, match="duplicate"):
        convert(raw([row, row]))
    with pytest.raises(ValueError, match="columns/units"):
        convert(raw(header=["Chuva (cm)" if h == "Chuva (mm)" else h for h in HEAD]))
