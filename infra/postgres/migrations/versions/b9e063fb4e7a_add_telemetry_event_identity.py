"""add telemetry event identity

Revision ID: b9e063fb4e7a
Revises: 3f523185ad04
Create Date: 2026-08-27 13:14:44.079250

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b9e063fb4e7a"
down_revision: str | Sequence[str] | None = "3f523185ad04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add deterministic event identity to telemetry."""

    op.add_column(
        "telemetry",
        sa.Column("event_id", sa.String(length=64), nullable=True),
    )

    op.create_unique_constraint(
        "uq_telemetry_event_id",
        "telemetry",
        ["event_id"],
    )


def downgrade() -> None:
    """Remove deterministic event identity from telemetry."""

    op.drop_constraint(
        "uq_telemetry_event_id",
        "telemetry",
        type_="unique",
    )

    op.drop_column("telemetry", "event_id")
