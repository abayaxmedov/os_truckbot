"""product sold_count

Revision ID: b2e7a3c5f019
Revises: a1f4c2d9e77b
Create Date: 2026-09-05 11:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2e7a3c5f019'
down_revision: Union[str, None] = 'a1f4c2d9e77b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'products',
        sa.Column('sold_count', sa.Integer(), nullable=False, server_default='0'),
    )
    # Backfill from existing order items (gross units sold).
    op.execute(
        """
        UPDATE products p
        SET sold_count = COALESCE(s.total, 0)
        FROM (
            SELECT product_id, SUM(quantity) AS total
            FROM order_items
            GROUP BY product_id
        ) s
        WHERE s.product_id = p.id
        """
    )


def downgrade() -> None:
    op.drop_column('products', 'sold_count')
