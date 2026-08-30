from datetime import UTC, datetime, timedelta

from services.ingestion.health.model import SourceHealth


class SourceHealthTracker:
    def __init__(
        self,
        *,
        source_id: str,
        stale_after_seconds: int = 1800,
    ) -> None:
        if stale_after_seconds <= 0:
            raise ValueError("stale_after_seconds must be greater than 0")

        self.stale_after_seconds = stale_after_seconds
        self.health = SourceHealth(source_id=source_id)

    def record_success(
        self,
        *,
        latest_observed_at: datetime,
        now: datetime | None = None,
    ) -> SourceHealth:
        current_time = now or datetime.now(UTC)

        self.health.last_success_at = current_time
        self.health.latest_observed_at = latest_observed_at
        self.health.consecutive_failures = 0
        self.health.last_error = None
        self.health.status = self._calculate_status(
            latest_observed_at=latest_observed_at,
            now=current_time,
        )

        return self.health

    def record_failure(
        self,
        *,
        error: Exception,
    ) -> SourceHealth:
        self.health.consecutive_failures += 1
        self.health.last_error = str(error)

        if self.health.latest_observed_at is None:
            self.health.status = "error"
        else:
            self.health.status = "stale"

        return self.health

    def refresh_status(
        self,
        *,
        now: datetime | None = None,
    ) -> SourceHealth:
        if self.health.latest_observed_at is None:
            return self.health

        current_time = now or datetime.now(UTC)

        self.health.status = self._calculate_status(
            latest_observed_at=self.health.latest_observed_at,
            now=current_time,
        )

        return self.health

    def _calculate_status(
        self,
        *,
        latest_observed_at: datetime,
        now: datetime,
    ) -> str:
        freshness = now - latest_observed_at

        if freshness <= timedelta(seconds=self.stale_after_seconds):
            return "healthy"

        return "stale"
