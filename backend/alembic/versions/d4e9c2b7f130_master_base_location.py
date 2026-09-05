"""master base location (lat/lng) — B5

Revision ID: d4e9c2b7f130
Revises: c3d8b1a6e42f
Create Date: 2026-09-05 13:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4e9c2b7f130'
down_revision: Union[str, None] = 'c3d8b1a6e42f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('master_profiles', sa.Column('latitude', sa.Numeric(10, 7), nullable=True))
    op.add_column('master_profiles', sa.Column('longitude', sa.Numeric(10, 7), nullable=True))


def downgrade() -> None:
    op.drop_column('master_profiles', 'longitude')
    op.drop_column('master_profiles', 'latitude')
