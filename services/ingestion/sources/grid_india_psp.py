import csv
import io
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from services.ingestion.models import CanonicalTelemetry

SOURCE_NAME = "grid_india_nldc_psp"
ENTITY_NAME = "all_india"

SOURCE_TIMEZONE = ZoneInfo("Asia/Kolkata")

REQUIRED_COLUMNS = {
    "TIME",
    "FREQUENCY (Hz)",
    "DEMAND MET (MW)",
}


class GridIndiaPspParseError(ValueError):
    """Raised when a GRID-INDIA PSP fixture cannot be parsed."""


def parse_grid_india_psp_csv(
    csv_text: str,
    *,
    report_date: date,
) -> list[CanonicalTelemetry]:
    reader = csv.DictReader(io.StringIO(csv_text))

    if reader.fieldnames is None:
        raise GridIndiaPspParseError("PSP input does not contain a header")

    missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise GridIndiaPspParseError(f"PSP input is missing required columns: {missing}")

    telemetry: list[CanonicalTelemetry] = []

    for row_number, row in enumerate(reader, start=2):
        if not any(value.strip() for value in row.values() if value):
            continue

        try:
            observed_at = _parse_observed_at(
                report_date=report_date,
                raw_time=row["TIME"],
            )

            frequency = float(row["FREQUENCY (Hz)"])
            demand_met = float(row["DEMAND MET (MW)"])

        except (TypeError, ValueError) as exc:
            raise GridIndiaPspParseError(f"Invalid PSP record at CSV row {row_number}") from exc

        telemetry.extend(
            [
                CanonicalTelemetry(
                    source=SOURCE_NAME,
                    entity=ENTITY_NAME,
                    metric="grid_frequency",
                    value=frequency,
                    unit="Hz",
                    observed_at=observed_at,
                ),
                CanonicalTelemetry(
                    source=SOURCE_NAME,
                    entity=ENTITY_NAME,
                    metric="demand_met",
                    value=demand_met,
                    unit="MW",
                    observed_at=observed_at,
                ),
            ]
        )

    return telemetry


def _parse_observed_at(
    *,
    report_date: date,
    raw_time: str,
) -> datetime:
    local_time = datetime.strptime(
        raw_time.strip(),
        "%H:%M",
    ).time()

    local_datetime = datetime.combine(
        report_date,
        local_time,
        tzinfo=SOURCE_TIMEZONE,
    )

    return local_datetime.astimezone(UTC)
