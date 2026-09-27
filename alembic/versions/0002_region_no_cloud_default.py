"""Remove the cloud-specific default for telemetry_events.region

The column was created with a server_default of "us-east-1". `region` remains a
valid provider-neutral telemetry field, but it must no longer default to a
specific cloud region. The application-side default is removed in the same
change; this migration only clears the database-side default.

Revision ID: 0002_region_no_cloud_default
Revises: 0001_initial_phase1
Create Date: 2026-09-27 00:00:00

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_region_no_cloud_default"
down_revision: str | None = "0001_initial_phase1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        "telemetry_events",
        "region",
        existing_type=sa.String(length=32),
        existing_nullable=True,
        server_default=None,
    )


def downgrade() -> None:
    # Restores the previous server_default so the migration is reversible.
    op.alter_column(
        "telemetry_events",
        "region",
        existing_type=sa.String(length=32),
        existing_nullable=True,
        server_default="us-east-1",
    )
