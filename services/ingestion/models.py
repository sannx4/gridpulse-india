from dataclasses import dataclass
from datetime import datetime
from typing import Literal

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

    def to_dict(self) -> dict[str, object]:
        return {
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
