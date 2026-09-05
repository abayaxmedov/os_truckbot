"""product manufacturing country

Revision ID: a1f4c2d9e77b
Revises: 86e2223ddb02
Create Date: 2026-09-05 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1f4c2d9e77b'
down_revision: Union[str, None] = '86e2223ddb02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'products',
        sa.Column('country', sa.String(length=64), nullable=False, server_default=''),
    )


def downgrade() -> None:
    op.drop_column('products', 'country')
