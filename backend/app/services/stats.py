from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SellerStatus
from app.models.order import Order, OrderItem, SellerOrder
from app.models.product import Product
from app.models.user import SellerProfile, User


async def get_admin_stats(session: AsyncSession) -> dict:
    orders_count = (await session.execute(select(func.count(Order.id)))).scalar_one()
    sales_total = (
        await session.execute(select(func.coalesce(func.sum(Order.total), 0)))
    ).scalar_one()
    commission_total = (
        await session.execute(select(func.coalesce(func.sum(SellerOrder.commission_amount), 0)))
    ).scalar_one()
    payout_total = (
        await session.execute(select(func.coalesce(func.sum(SellerOrder.seller_payout), 0)))
    ).scalar_one()
    customers_count = (await session.execute(select(func.count(User.id)))).scalar_one()
    sellers_count = (
        await session.execute(
            select(func.count(SellerProfile.id)).where(SellerProfile.status == SellerStatus.active)
        )
    ).scalar_one()
    products_count = (await session.execute(select(func.count(Product.id)))).scalar_one()

    return {
        "orders_count": int(orders_count or 0),
        "sales_total": Decimal(str(sales_total or 0)),
        "commission_total": Decimal(str(commission_total or 0)),  # marketplace profit
        "payout_total": Decimal(str(payout_total or 0)),
        "customers_count": int(customers_count or 0),
        "sellers_count": int(sellers_count or 0),
        "products_count": int(products_count or 0),
    }


async def get_popular_products(session: AsyncSession, limit: int = 10) -> list[dict]:
    """Top products by total units sold (fallback to views if no sales)."""
    result = await session.execute(
        select(
            Product.id,
            Product.name_ru,
            Product.article,
            func.coalesce(func.sum(OrderItem.quantity), 0).label("sold"),
            Product.views,
        )
        .outerjoin(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.id)
        .order_by(func.coalesce(func.sum(OrderItem.quantity), 0).desc(), Product.views.desc())
        .limit(limit)
    )
    return [
        {
            "id": r.id,
            "name_ru": r.name_ru,
            "article": r.article,
            "sold": int(r.sold),
            "views": r.views,
        }
        for r in result.all()
    ]


async def get_seller_stats(session: AsyncSession, seller_id: int) -> dict:
    sales_total = (
        await session.execute(
            select(func.coalesce(func.sum(SellerOrder.subtotal), 0)).where(
                SellerOrder.seller_id == seller_id
            )
        )
    ).scalar_one()
    commission_total = (
        await session.execute(
            select(func.coalesce(func.sum(SellerOrder.commission_amount), 0)).where(
                SellerOrder.seller_id == seller_id
            )
        )
    ).scalar_one()
    payout_total = (
        await session.execute(
            select(func.coalesce(func.sum(SellerOrder.seller_payout), 0)).where(
                SellerOrder.seller_id == seller_id
            )
        )
    ).scalar_one()
    orders_count = (
        await session.execute(
            select(func.count(SellerOrder.id)).where(SellerOrder.seller_id == seller_id)
        )
    ).scalar_one()
    products_count = (
        await session.execute(select(func.count(Product.id)).where(Product.seller_id == seller_id))
    ).scalar_one()

    return {
        "sales_total": Decimal(str(sales_total or 0)),
        "commission_total": Decimal(str(commission_total or 0)),
        "payout_total": Decimal(str(payout_total or 0)),
        "orders_count": int(orders_count or 0),
        "products_count": int(products_count or 0),
    }
