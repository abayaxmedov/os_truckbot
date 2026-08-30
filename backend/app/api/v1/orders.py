from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.serializers import serialize_order, serialize_order_list_item
from app.core.deps import CurrentUser, SessionDep
from app.models.order import Order, OrderItem, SellerOrder
from app.models.product import Product
from app.schemas.common import Page
from app.schemas.order import (
    OrderCreate,
    OrderListItem,
    OrderOut,
    PayRequest,
    PayResponse,
)
from app.services import notifications
from app.services.orders import CheckoutInput, OrderError, create_order
from app.services.payment_service import start_payment

router = APIRouter(prefix="/orders", tags=["orders"])
logger = logging.getLogger(__name__)

_ORDER_LOAD = (
    selectinload(Order.seller_orders)
    .selectinload(SellerOrder.items)
    .selectinload(OrderItem.product)
    .selectinload(Product.images),
    selectinload(Order.seller_orders).selectinload(SellerOrder.seller),
    selectinload(Order.seller_orders).selectinload(SellerOrder.review),
)


async def _load_order(session: SessionDep, order_id: int) -> Order | None:
    result = await session.execute(select(Order).where(Order.id == order_id).options(*_ORDER_LOAD))
    return result.scalar_one_or_none()


@router.post("", response_model=OrderOut)
async def checkout(payload: OrderCreate, session: SessionDep, user: CurrentUser) -> OrderOut:
    try:
        order = await create_order(
            session,
            user,
            CheckoutInput(
                contact_name=payload.contact_name,
                phone=payload.phone,
                city=payload.city,
                address=payload.address,
                comment=payload.comment,
                latitude=payload.latitude,
                longitude=payload.longitude,
                delivery_method=payload.delivery_method,
                payment_method=payload.payment_method,
            ),
        )
        await start_payment(session, order, payload.payment_method)
        await session.commit()
    except OrderError as exc:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        await notifications.notify_new_order(session, order.id)
    except Exception:  # noqa: BLE001 - notifications must never break checkout
        logger.exception("Failed to send new-order notifications for order %s", order.id)

    loaded = await _load_order(session, order.id)
    return serialize_order(loaded, is_buyer=True)


@router.get("", response_model=Page[OrderListItem])
async def list_orders(
    session: SessionDep,
    user: CurrentUser,
    page: int = 1,
    page_size: int = 20,
) -> Page[OrderListItem]:
    total = (
        await session.execute(select(func.count(Order.id)).where(Order.buyer_id == user.id))
    ).scalar_one()
    result = await session.execute(
        select(Order)
        .where(Order.buyer_id == user.id)
        .options(
            selectinload(Order.seller_orders).selectinload(SellerOrder.items),
        )
        .order_by(Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = [serialize_order_list_item(o) for o in result.scalars().unique().all()]
    return Page[OrderListItem](items=items, total=int(total), page=page, page_size=page_size)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, session: SessionDep, user: CurrentUser) -> OrderOut:
    order = await _load_order(session, order_id)
    if order is None or order.buyer_id != user.id:
        raise HTTPException(status_code=404, detail="order_not_found")
    return serialize_order(order, is_buyer=True)


@router.post("/{order_id}/pay", response_model=PayResponse)
async def pay_order(
    order_id: int, payload: PayRequest, session: SessionDep, user: CurrentUser
) -> PayResponse:
    order = await session.get(Order, order_id)
    if order is None or order.buyer_id != user.id:
        raise HTTPException(status_code=404, detail="order_not_found")
    payment = await start_payment(session, order, payload.provider)
    await session.commit()
    return PayResponse(
        payment_url=payment.payment_url,
        provider=payment.provider.value,
        status=payment.status.value,
    )
