from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.utils import normalize_part_number
from app.models.analog import AnalogReference
from app.models.enums import ProductStatus
from app.models.product import Product


async def find_analog_numbers(session: AsyncSession, number: str) -> list[AnalogReference]:
    """Return all references cross-referenced with the given part number."""
    norm = normalize_part_number(number)
    if not norm:
        return []
    group_ids_subq = (
        select(AnalogReference.group_id).where(AnalogReference.number == norm).scalar_subquery()
    )
    result = await session.execute(
        select(AnalogReference)
        .where(AnalogReference.group_id.in_(group_ids_subq))
        .order_by(AnalogReference.is_original.desc(), AnalogReference.brand)
    )
    return list(result.scalars().all())


async def find_analog_products(
    session: AsyncSession, number: str, exclude_product_id: int | None = None
) -> list[Product]:
    """Find active products whose article/oem matches the number or any of its analogs."""
    norm = normalize_part_number(number)
    if not norm:
        return []

    group_ids_subq = (
        select(AnalogReference.group_id).where(AnalogReference.number == norm).scalar_subquery()
    )
    numbers_subq = (
        select(AnalogReference.number)
        .where(AnalogReference.group_id.in_(group_ids_subq))
        .scalar_subquery()
    )

    conditions = [
        Product.article_norm == norm,
        Product.oem_norm == norm,
        Product.article_norm.in_(numbers_subq),
        Product.oem_norm.in_(numbers_subq),
    ]
    stmt = (
        select(Product)
        .where(
            Product.is_active.is_(True),
            Product.status == ProductStatus.approved,
            or_(*conditions),
        )
        .options(
            selectinload(Product.images),
            selectinload(Product.seller),
        )
        .limit(100)
    )
    if exclude_product_id is not None:
        stmt = stmt.where(Product.id != exclude_product_id)

    result = await session.execute(stmt)
    return list(result.scalars().unique().all())
