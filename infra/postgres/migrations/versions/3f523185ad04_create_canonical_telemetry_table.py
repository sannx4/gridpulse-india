"""create canonical telemetry table

Revision ID: 3f523185ad04
Revises: 27c015ebfa5e
Create Date: 2026-08-24 19:43:28.845524

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3f523185ad04"
down_revision: str | Sequence[str] | None = "27c015ebfa5e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "telemetry",
        sa.Column(
            "id",
            sa.BigInteger(),
            sa.Identity(),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "entity",
            sa.String(length=128),
            nullable=False,
        ),
        sa.Column(
            "metric",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "value",
            sa.Double(),
            nullable=False,
        ),
        sa.Column(
            "unit",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "observed_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "ingested_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "quality",
            sa.String(length=16),
            server_default=sa.text("'unknown'"),
            nullable=False,
        ),
        sa.Column(
            "schema_version",
            sa.SmallInteger(),
            server_default=sa.text("1"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quality IN ('good', 'suspect', 'bad', 'estimated', 'unknown')",
            name="ck_telemetry_quality",
        ),
        sa.CheckConstraint(
            "schema_version >= 1",
            name="ck_telemetry_schema_version",
        ),
        sa.PrimaryKeyConstraint(
            "id",
            "observed_at",
            name="pk_telemetry",
        ),
    )


def downgrade() -> None:
    op.drop_table("telemetry")
