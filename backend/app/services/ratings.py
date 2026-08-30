from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import OrderStatus
from app.models.order import SellerOrder
from app.models.review import Review
from app.models.user import SellerProfile


class ReviewError(ValueError):
    pass


async def recompute_seller_stats(session: AsyncSession, seller_id: int) -> None:
    seller = await session.get(SellerProfile, seller_id)
    if seller is None:
        return

    # Review aggregates
    avg_stars, review_count = (
        await session.execute(
            select(func.avg(Review.stars), func.count(Review.id)).where(
                Review.seller_id == seller_id
            )
        )
    ).one()

    # Order aggregates by status
    rows = (
        await session.execute(
            select(SellerOrder.status, func.count(SellerOrder.id))
            .where(SellerOrder.seller_id == seller_id)
            .group_by(SellerOrder.status)
        )
    ).all()
    counts = {status: cnt for status, cnt in rows}
    total = sum(counts.values())
    completed = counts.get(OrderStatus.completed, 0)
    cancelled = counts.get(OrderStatus.cancelled, 0)
    final = completed + cancelled

    seller.rating = (
        Decimal(str(round(float(avg_stars), 2))) if avg_stars is not None else Decimal("0")
    )
    seller.reviews_count = int(review_count or 0)
    seller.orders_count = int(total)
    seller.completion_rate = (
        Decimal(str(round(completed / final * 100, 2))) if final else Decimal("0")
    )
    await session.flush()


async def add_review(
    session: AsyncSession,
    buyer_id: int,
    seller_order: SellerOrder,
    stars: int,
    comment: str = "",
) -> Review:
    if stars < 1 or stars > 5:
        raise ReviewError("stars_out_of_range")
    if seller_order.status != OrderStatus.completed:
        raise ReviewError("order_not_completed")

    existing = await session.execute(
        select(Review).where(Review.seller_order_id == seller_order.id)
    )
    if existing.scalar_one_or_none() is not None:
        raise ReviewError("already_reviewed")

    review = Review(
        seller_order_id=seller_order.id,
        buyer_id=buyer_id,
        seller_id=seller_order.seller_id,
        stars=stars,
        comment=comment,
    )
    session.add(review)
    await session.flush()
    await recompute_seller_stats(session, seller_order.seller_id)
    return review
