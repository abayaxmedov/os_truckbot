from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem
from app.models.enums import DeliveryMethod, OrderStatus, PaymentProvider, ProductStatus
from app.models.order import Order, OrderItem, SellerOrder
from app.models.product import Product
from app.models.user import User
from app.services.commission import resolve_product_commission, split_amount
from app.services.settings_service import get_default_delivery_cost


class OrderError(ValueError):
    """Raised for invalid checkout (empty cart, out of stock, etc.)."""


@dataclass
class CheckoutInput:
    contact_name: str
    phone: str
    city: str = ""
    address: str = ""
    comment: str = ""
    latitude: float | None = None
    longitude: float | None = None
    delivery_method: DeliveryMethod = DeliveryMethod.delivery
    payment_method: PaymentProvider = PaymentProvider.cash


async def get_or_create_cart(session: AsyncSession, user_id: int) -> Cart:
    result = await session.execute(
        select(Cart).where(Cart.user_id == user_id).options(selectinload(Cart.items))
    )
    cart = result.scalar_one_or_none()
    if cart is None:
        cart = Cart(user_id=user_id)
        session.add(cart)
        await session.flush()
    return cart


async def _load_cart_for_checkout(session: AsyncSession, user_id: int) -> Cart:
    result = await session.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.seller),
            selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.category),
        )
    )
    cart = result.scalar_one_or_none()
    if cart is None or not cart.items:
        raise OrderError("cart_empty")
    return cart


async def create_order(session: AsyncSession, user: User, data: CheckoutInput) -> Order:
    cart = await _load_cart_for_checkout(session, user.id)
    delivery_cost = await get_default_delivery_cost(session)

    # Group cart items by seller
    groups: dict[int, list[CartItem]] = {}
    for item in cart.items:
        product = item.product
        if product is None or not product.is_active or product.status != ProductStatus.approved:
            raise OrderError(f"product_unavailable:{item.product_id}")
        if item.quantity < 1:
            raise OrderError(f"bad_quantity:{item.product_id}")
        if product.stock_qty < item.quantity:
            raise OrderError(f"out_of_stock:{item.product_id}")
        groups.setdefault(product.seller_id, []).append(item)

    order = Order(
        buyer_id=user.id,
        contact_name=data.contact_name,
        phone=data.phone,
        city=data.city,
        address=data.address,
        comment=data.comment,
        latitude=data.latitude,
        longitude=data.longitude,
        delivery_method=data.delivery_method,
        payment_method=data.payment_method,
        delivery_cost=delivery_cost,
        subtotal=Decimal("0"),
        discount=Decimal("0"),
        total=Decimal("0"),
    )
    # Keep `order` pending (not yet flushed) so its relationship collections stay
    # initialized in memory; sub-orders/items are wired via relationships below and
    # cascade-persist on the final flush. This avoids a lazy load when the caller
    # reads order.seller_orders without a reload.
    session.add(order)

    order_subtotal = Decimal("0")
    for seller_id, items in groups.items():
        seller_order = SellerOrder(
            order=order,
            seller_id=seller_id,
            status=OrderStatus.new,
            subtotal=Decimal("0"),
            commission_amount=Decimal("0"),
            seller_payout=Decimal("0"),
        )
        session.add(seller_order)

        seller_subtotal = Decimal("0")
        seller_commission = Decimal("0")
        for item in items:
            product = item.product
            percent = await resolve_product_commission(
                session, product, product.seller, product.category
            )
            line_total = (Decimal(product.price) * item.quantity).quantize(Decimal("0.01"))
            commission, _payout = split_amount(line_total, percent)

            session.add(
                OrderItem(
                    seller_order=seller_order,
                    product_id=product.id,
                    product_name=product.name_ru,
                    article=product.article,
                    unit_price=product.price,
                    quantity=item.quantity,
                    line_total=line_total,
                    commission_percent=percent,
                    bonus=product.bonus or Decimal("0"),
                )
            )
            product.stock_qty -= item.quantity
            product.sold_count = (product.sold_count or 0) + item.quantity
            seller_subtotal += line_total
            seller_commission += commission

        seller_order.subtotal = seller_subtotal
        seller_order.commission_amount = seller_commission
        seller_order.seller_payout = seller_subtotal - seller_commission
        order_subtotal += seller_subtotal

    order.subtotal = order_subtotal
    order.total = order_subtotal + delivery_cost - order.discount

    # Clear the cart
    for item in list(cart.items):
        await session.delete(item)

    await session.flush()

    # If the buyer is a "master" (usta), record per-product bonuses as pending.
    from app.models.master import MasterProfile
    from app.services.bonus import credit_pending_on_checkout

    master = (
        await session.execute(select(MasterProfile).where(MasterProfile.user_id == user.id))
    ).scalar_one_or_none()
    if master is not None:
        await credit_pending_on_checkout(session, order, master)

    return order


async def update_seller_order_status(
    session: AsyncSession, seller_order: SellerOrder, new_status: OrderStatus
) -> SellerOrder:
    seller_order.status = new_status
    await session.flush()
    if new_status in (OrderStatus.completed, OrderStatus.cancelled):
        from app.services.bonus import settle_seller_order_bonus
        from app.services.ratings import recompute_seller_stats

        await settle_seller_order_bonus(session, seller_order, new_status)
        await recompute_seller_stats(session, seller_order.seller_id)
    return seller_order
