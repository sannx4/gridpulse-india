from datetime import UTC, datetime, timedelta

from services.ingestion.health.tracker import SourceHealthTracker


def test_new_source_starts_stale() -> None:
    tracker = SourceHealthTracker(
        source_id="grid_india_nldc_psp",
    )

    health = tracker.health

    assert health.source_id == "grid_india_nldc_psp"
    assert health.last_success_at is None
    assert health.latest_observed_at is None
    assert health.consecutive_failures == 0
    assert health.status == "stale"
    assert health.last_error is None


def test_success_marks_source_healthy() -> None:
    tracker = SourceHealthTracker(
        source_id="grid_india_nldc_psp",
    )

    now = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
    observed_at = now - timedelta(minutes=5)

    health = tracker.record_success(
        latest_observed_at=observed_at,
        now=now,
    )

    assert health.last_success_at == now
    assert health.latest_observed_at == observed_at
    assert health.consecutive_failures == 0
    assert health.status == "healthy"
    assert health.last_error is None


def test_failure_increments_consecutive_failures() -> None:
    tracker = SourceHealthTracker(
        source_id="grid_india_nldc_psp",
    )

    error = TimeoutError("connection timed out")

    health = tracker.record_failure(error=error)

    assert health.consecutive_failures == 1
    assert health.last_error == "connection timed out"
    assert health.status == "error"


def test_repeated_failures_increment_counter() -> None:
    tracker = SourceHealthTracker(
        source_id="grid_india_nldc_psp",
    )

    tracker.record_failure(
        error=TimeoutError("timeout"),
    )
    tracker.record_failure(
        error=TimeoutError("timeout"),
    )

    health = tracker.record_failure(
        error=TimeoutError("timeout"),
    )

    assert health.consecutive_failures == 3


def test_success_resets_failures() -> None:
    tracker = SourceHealthTracker(
        source_id="grid_india_nldc_psp",
    )

    tracker.record_failure(
        error=TimeoutError("timeout"),
    )
    tracker.record_failure(
        error=TimeoutError("timeout"),
    )

    now = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)

    health = tracker.record_success(
        latest_observed_at=now - timedelta(minutes=5),
        now=now,
    )

    assert health.consecutive_failures == 0
    assert health.last_error is None
    assert health.status == "healthy"


def test_old_data_becomes_stale() -> None:
    tracker = SourceHealthTracker(
        source_id="grid_india_nldc_psp",
        stale_after_seconds=1800,
    )

    now = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
    observed_at = now - timedelta(minutes=31)

    health = tracker.record_success(
        latest_observed_at=observed_at,
        now=now,
    )

    assert health.status == "stale"


def test_fresh_data_is_healthy() -> None:
    tracker = SourceHealthTracker(
        source_id="grid_india_nldc_psp",
        stale_after_seconds=1800,
    )

    now = datetime(2026, 8, 30, 12, 0, tzinfo=UTC)
    observed_at = now - timedelta(minutes=10)

    health = tracker.record_success(
        latest_observed_at=observed_at,
        now=now,
    )

    assert health.status == "healthy"
