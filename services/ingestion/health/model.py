from dataclasses import dataclass
from datetime import datetime
from typing import Literal

SourceStatus = Literal["healthy", "stale", "error"]


@dataclass(slots=True)
class SourceHealth:
    source_id: str
    last_success_at: datetime | None = None
    latest_observed_at: datetime | None = None
    consecutive_failures: int = 0
    status: SourceStatus = "stale"
    last_error: str | None = None
