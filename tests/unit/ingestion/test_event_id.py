from datetime import UTC, date, datetime, timedelta, timezone
from pathlib import Path

import pytest

from services.ingestion.identity import generate_event_id
from services.ingestion.models import CanonicalTelemetry
from services.ingestion.sources.grid_india_psp import (
    parse_grid_india_psp_csv,
)


def test_identical_identity_produces_identical_event_id() -> None:
    observed_at = datetime(
        2026,
        8,
        19,
        17,
        0,
        tzinfo=UTC,
    )

    first = generate_event_id(
        source="grid_india_nldc_psp",
        entity="all_india",
        metric="grid_frequency",
        observed_at=observed_at,
    )

    second = generate_event_id(
        source="grid_india_nldc_psp",
        entity="all_india",
        metric="grid_frequency",
        observed_at=observed_at,
    )

    assert first == second


def test_corrected_value_keeps_same_event_id() -> None:
    observed_at = datetime(
        2026,
        8,
        19,
        17,
        0,
        tzinfo=UTC,
    )

    original = CanonicalTelemetry(
        source="grid_india_nldc_psp",
        entity="all_india",
        metric="grid_frequency",
        value=50.01,
        unit="Hz",
        observed_at=observed_at,
        quality="unknown",
    )

    corrected = CanonicalTelemetry(
        source="grid_india_nldc_psp",
        entity="all_india",
        metric="grid_frequency",
        value=49.99,
        unit="Hz",
        observed_at=observed_at,
        quality="good",
    )

    assert original.event_id == corrected.event_id


def test_different_metric_produces_different_event_id() -> None:
    observed_at = datetime(
        2026,
        8,
        19,
        17,
        0,
        tzinfo=UTC,
    )

    frequency_id = generate_event_id(
        source="grid_india_nldc_psp",
        entity="all_india",
        metric="grid_frequency",
        observed_at=observed_at,
    )

    demand_id = generate_event_id(
        source="grid_india_nldc_psp",
        entity="all_india",
        metric="demand_met",
        observed_at=observed_at,
    )

    assert frequency_id != demand_id


def test_same_instant_in_different_timezone_has_same_event_id() -> None:
    ist = timezone(
        timedelta(
            hours=5,
            minutes=30,
        )
    )

    utc_time = datetime(
        2026,
        8,
        19,
        17,
        0,
        tzinfo=UTC,
    )

    ist_time = datetime(
        2026,
        8,
        19,
        22,
        30,
        tzinfo=ist,
    )

    utc_id = generate_event_id(
        source="grid_india_nldc_psp",
        entity="all_india",
        metric="grid_frequency",
        observed_at=utc_time,
    )

    ist_id = generate_event_id(
        source="grid_india_nldc_psp",
        entity="all_india",
        metric="grid_frequency",
        observed_at=ist_time,
    )

    assert utc_id == ist_id


def test_naive_datetime_is_rejected() -> None:
    naive_time = datetime(
        2026,
        8,
        19,
        17,
        0,
    )

    with pytest.raises(
        ValueError,
        match="timezone-aware",
    ):
        generate_event_id(
            source="grid_india_nldc_psp",
            entity="all_india",
            metric="grid_frequency",
            observed_at=naive_time,
        )


def test_reprocessing_fixture_produces_identical_event_ids() -> None:
    fixture_path = Path("tests/fixtures/grid_india/psp_2026-08-19_15min.csv")

    raw_csv = fixture_path.read_text(encoding="utf-8")

    first_run = parse_grid_india_psp_csv(
        raw_csv,
        report_date=date(2026, 8, 19),
    )

    second_run = parse_grid_india_psp_csv(
        raw_csv,
        report_date=date(2026, 8, 19),
    )

    first_ids = [item.event_id for item in first_run]

    second_ids = [item.event_id for item in second_run]

    assert first_ids == second_ids
    assert len(first_ids) == 6
    assert len(set(first_ids)) == 6
