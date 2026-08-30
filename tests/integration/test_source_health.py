from services.ingestion.health.tracker import SourceHealthTracker
from services.ingestion.http.exceptions import SourceNetworkError


def test_source_failure_is_recorded_without_killing_health_tracker() -> None:
    tracker = SourceHealthTracker(
        source_id="grid_india_nldc_psp",
    )

    error = SourceNetworkError(
        "Source network request failed",
        source="grid_india_nldc_psp",
        url="http://127.0.0.1:9/unavailable",
        request_id="test-request",
    )

    health = tracker.record_failure(error=error)

    assert health.source_id == "grid_india_nldc_psp"
    assert health.consecutive_failures == 1
    assert health.last_error is not None
    assert health.status == "error"
