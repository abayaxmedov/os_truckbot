from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import selectinload

from app.api.serializers import serialize_message, serialize_review
from app.core.deps import CurrentUser, SessionDep
from app.models.message import Message
from app.models.order import Order, SellerOrder
from app.models.product import Product
from app.models.review import Review
from app.schemas.misc import MessageCreate, MessageOut, ReviewCreate, ReviewOut
from app.services import notifications
from app.services.ratings import ReviewError, add_review

router = APIRouter(tags=["interactions"])
logger = logging.getLogger(__name__)


# ---- Reviews ----
@router.post("/reviews", response_model=ReviewOut)
async def create_review(payload: ReviewCreate, session: SessionDep, user: CurrentUser) -> ReviewOut:
    result = await session.execute(
        select(SellerOrder)
        .where(SellerOrder.id == payload.seller_order_id)
        .options(selectinload(SellerOrder.order))
    )
    so = result.scalar_one_or_none()
    if so is None or so.order is None or so.order.buyer_id != user.id:
        raise HTTPException(status_code=404, detail="order_not_found")
    try:
        review = await add_review(session, user.id, so, payload.stars, payload.comment)
        await session.commit()
    except ReviewError as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return serialize_review(review)


@router.get("/reviews/seller/{seller_id}", response_model=list[ReviewOut])
async def seller_reviews(seller_id: int, session: SessionDep) -> list[ReviewOut]:
    result = await session.execute(
        select(Review).where(Review.seller_id == seller_id).order_by(Review.id.desc()).limit(100)
    )
    return [serialize_review(r) for r in result.scalars().all()]


# ---- Messages ----
@router.post("/messages", response_model=MessageOut)
async def send_message(
    payload: MessageCreate, session: SessionDep, user: CurrentUser
) -> MessageOut:
    to_user_id = payload.to_user_id

    # Resolve recipient from product (seller) if not given
    if to_user_id is None and payload.product_id is not None:
        product = await session.get(
            Product, payload.product_id, options=[selectinload(Product.seller)]
        )
        if product is None or product.seller is None:
            raise HTTPException(status_code=404, detail="product_not_found")
        to_user_id = product.seller.user_id

    # Resolve recipient from order (buyer) if seller replies
    if to_user_id is None and payload.order_id is not None:
        order = await session.get(Order, payload.order_id)
        if order is None:
            raise HTTPException(status_code=404, detail="order_not_found")
        to_user_id = order.buyer_id

    if to_user_id is None:
        raise HTTPException(status_code=400, detail="recipient_required")
    if to_user_id == user.id:
        raise HTTPException(status_code=400, detail="cannot_message_self")

    message = Message(
        from_user_id=user.id,
        to_user_id=to_user_id,
        kind=payload.kind,
        product_id=payload.product_id,
        order_id=payload.order_id,
        text=payload.text,
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    try:
        await notifications.notify_new_message(session, message.id)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to notify recipient about message %s", message.id)
    return serialize_message(message)


@router.get("/messages", response_model=list[MessageOut])
async def list_messages(session: SessionDep, user: CurrentUser) -> list[MessageOut]:
    result = await session.execute(
        select(Message)
        .where(or_(Message.from_user_id == user.id, Message.to_user_id == user.id))
        .order_by(Message.id.desc())
        .limit(200)
    )
    return [serialize_message(m) for m in result.scalars().all()]
