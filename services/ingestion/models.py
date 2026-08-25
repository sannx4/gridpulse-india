from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from services.ingestion.identity import generate_event_id

TelemetryQuality = Literal[
    "good",
    "suspect",
    "bad",
    "estimated",
    "unknown",
]


@dataclass(frozen=True, slots=True)
class CanonicalTelemetry:
    source: str
    entity: str
    metric: str
    value: float
    unit: str
    observed_at: datetime
    quality: TelemetryQuality = "unknown"
    schema_version: int = 1
    ingested_at: datetime | None = None

    @property
    def event_id(self) -> str:
        return generate_event_id(
            source=self.source,
            entity=self.entity,
            metric=self.metric,
            observed_at=self.observed_at,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "event_id": self.event_id,
            "source": self.source,
            "entity": self.entity,
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "observed_at": self.observed_at.isoformat(),
            "ingested_at": (self.ingested_at.isoformat() if self.ingested_at is not None else None),
            "quality": self.quality,
            "schema_version": self.schema_version,
        }
