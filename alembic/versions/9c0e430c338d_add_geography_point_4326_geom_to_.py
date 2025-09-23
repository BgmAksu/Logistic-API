"""add geography(Point,4326) geom to addresses

Revision ID: 9c0e430c338d
Revises: 5d47f9f41f3f
Create Date: 2025-09-23 09:55:05.256847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = '9c0e430c338d'
down_revision: Union[str, Sequence[str], None] = '5d47f9f41f3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add column if not exists (PostgreSQL)
    op.execute(
        "ALTER TABLE addresses "
        "ADD COLUMN IF NOT EXISTS geom geography(POINT,4326)"
    )
    # Create GiST index if not exists
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_addresses_geom "
        "ON addresses USING gist (geom)"
    )

def downgrade() -> None:
    # Drop index/column if exists
    op.execute("DROP INDEX IF EXISTS idx_addresses_geom")
    op.execute("ALTER TABLE addresses DROP COLUMN IF EXISTS geom")
