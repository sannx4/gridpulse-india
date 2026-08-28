import os
from datetime import date

from services.ingestion.db.repository import TelemetryRepository
from services.ingestion.http.client import SourceHttpClient
from services.ingestion.sources.grid_india_psp import parse_grid_india_psp_csv

SOURCE_NAME = "grid_india_nldc_psp"


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    source_url = os.getenv("GRID_INDIA_PSP_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")

    if not source_url:
        raise RuntimeError("GRID_INDIA_PSP_URL is not configured")

    report_date = date.today()

    repository = TelemetryRepository(database_url)

    try:
        with SourceHttpClient(source=SOURCE_NAME) as client:
            response = client.get(source_url)

            telemetry = parse_grid_india_psp_csv(
                response.text,
                report_date=report_date,
            )

        inserted = 0
        duplicates = 0

        for record in telemetry:
            if repository.insert(record):
                inserted += 1
            else:
                duplicates += 1

        print(
            f"Ingestion complete: "
            f"records={len(telemetry)}, "
            f"inserted={inserted}, "
            f"duplicates={duplicates}"
        )

    finally:
        repository.close()


if __name__ == "__main__":
    main()
