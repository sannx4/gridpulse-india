import hashlib
import json
from datetime import UTC, datetime


def generate_event_id(
    *,
    source: str,
    entity: str,
    metric: str,
    observed_at: datetime,
) -> str:
    """Generate a deterministic identity for one logical telemetry observation."""

    if observed_at.tzinfo is None or observed_at.utcoffset() is None:
        raise ValueError("observed_at must be timezone-aware")

    observed_at_utc = observed_at.astimezone(UTC)

    canonical_timestamp = observed_at_utc.isoformat(timespec="microseconds").replace(
        "+00:00",
        "Z",
    )

    identity = {
        "source": source,
        "entity": entity,
        "metric": metric,
        "observed_at": canonical_timestamp,
    }

    canonical_identity = json.dumps(
        identity,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )

    return hashlib.sha256(canonical_identity.encode("utf-8")).hexdigest()
