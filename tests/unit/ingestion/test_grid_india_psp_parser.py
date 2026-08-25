import json
from datetime import date
from pathlib import Path

import pytest

from services.ingestion.sources.grid_india_psp import (
    GridIndiaPspParseError,
    parse_grid_india_psp_csv,
)

FIXTURE_PATH = Path("tests/fixtures/grid_india/psp_2026-08-19_15min.csv")

GOLDEN_PATH = Path("tests/golden/grid_india/psp_2026-08-19_expected.json")


def test_grid_india_psp_fixture_matches_golden_file() -> None:
    raw_csv = FIXTURE_PATH.read_text(encoding="utf-8")

    expected = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))

    telemetry = parse_grid_india_psp_csv(
        raw_csv,
        report_date=date(2026, 8, 19),
    )

    actual = [item.to_dict() for item in telemetry]

    assert actual == expected


def test_grid_india_psp_parser_creates_two_metrics_per_row() -> None:
    raw_csv = FIXTURE_PATH.read_text(encoding="utf-8")

    telemetry = parse_grid_india_psp_csv(
        raw_csv,
        report_date=date(2026, 8, 19),
    )

    assert len(telemetry) == 6

    assert {item.metric for item in telemetry} == {
        "grid_frequency",
        "demand_met",
    }


def test_grid_india_psp_parser_rejects_missing_columns() -> None:
    raw_csv = """TIME,FREQUENCY (Hz)
22:30,50.01
"""

    with pytest.raises(
        GridIndiaPspParseError,
        match="missing required columns",
    ):
        parse_grid_india_psp_csv(
            raw_csv,
            report_date=date(2026, 8, 19),
        )


def test_grid_india_psp_parser_rejects_invalid_value() -> None:
    raw_csv = """TIME,FREQUENCY (Hz),DEMAND MET (MW)
22:30,not-a-number,237892
"""

    with pytest.raises(
        GridIndiaPspParseError,
        match="Invalid PSP record",
    ):
        parse_grid_india_psp_csv(
            raw_csv,
            report_date=date(2026, 8, 19),
        )
