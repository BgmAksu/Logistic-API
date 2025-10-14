"""add indexes for shipments and tracking_events

Revision ID: e2fd3ff02cb0
Revises: 9c0e430c338d
Create Date: 2025-10-14 11:41:36.585634

"""

from typing import Union
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2fd3ff02cb0"
down_revision: str | Sequence[str] | None = "9c0e430c338d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS ix_shipments_status ON shipments (status)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_shipments_planned_date ON shipments (planned_delivery_date)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_tracking_events_parcel_time ON tracking_events (parcel_id, event_time)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_tracking_events_parcel_time")
    op.execute("DROP INDEX IF EXISTS ix_shipments_planned_date")
    op.execute("DROP INDEX IF EXISTS ix_shipments_status")
