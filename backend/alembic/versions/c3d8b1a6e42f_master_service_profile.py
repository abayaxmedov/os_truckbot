"""master service profile fields (B1)

Revision ID: c3d8b1a6e42f
Revises: b2e7a3c5f019
Create Date: 2026-09-05 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c3d8b1a6e42f'
down_revision: Union[str, None] = 'b2e7a3c5f019'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('master_profiles', sa.Column('trucks', sa.String(length=255), nullable=False, server_default=''))
    op.add_column('master_profiles', sa.Column('specializations', sa.String(length=512), nullable=False, server_default=''))
    op.add_column('master_profiles', sa.Column('regions', sa.String(length=255), nullable=False, server_default=''))
    op.add_column('master_profiles', sa.Column('work_hours', sa.String(length=64), nullable=False, server_default=''))
    op.add_column('master_profiles', sa.Column('is_24_7', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('master_profiles', sa.Column('experience_years', sa.Integer(), nullable=True))
    op.add_column('master_profiles', sa.Column('bio', sa.Text(), nullable=False, server_default=''))
    op.add_column('master_profiles', sa.Column('price_call', sa.Numeric(14, 2), nullable=True))
    op.add_column('master_profiles', sa.Column('price_diagnostics', sa.Numeric(14, 2), nullable=True))
    op.add_column('master_profiles', sa.Column('price_repair_note', sa.String(length=64), nullable=False, server_default=''))
    op.add_column('master_profiles', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    for col in (
        'is_verified', 'price_repair_note', 'price_diagnostics', 'price_call',
        'bio', 'experience_years', 'is_24_7', 'work_hours', 'regions',
        'specializations', 'trucks',
    ):
        op.drop_column('master_profiles', col)
