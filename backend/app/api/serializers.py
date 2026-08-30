from __future__ import annotations

from decimal import Decimal

from app.models.banner import Banner
from app.models.cart import Cart
from app.models.catalog import Category, TruckBrand
from app.models.enums import OrderStatus
from app.models.message import Message
from app.models.order import Order, OrderItem, SellerOrder
from app.models.product import Product
from app.models.review import Review
from app.models.user import SellerProfile
from app.schemas.admin import BannerOut
from app.schemas.cart import CartItemOut, CartOut
from app.schemas.catalog import CategoryOut, TruckBrandOut, TruckModelOut
from app.schemas.misc import MessageOut, ReviewOut
from app.schemas.order import (
    OrderItemOut,
    OrderListItem,
    OrderOut,
    SellerOrderOut,
    SellerOrderRow,
)
from app.schemas.product import (
    ProductImageOut,
    ProductListItem,
    ProductOut,
    SellerBrief,
    VehicleOut,
)
from app.services.media import media_url


def _dec(value: Decimal | float | int | None) -> float:
    return float(value) if value is not None else 0.0


# ---- Catalog ----
def serialize_brand(b: TruckBrand) -> TruckBrandOut:
    return TruckBrandOut(
        id=b.id,
        name=b.name,
        slug=b.slug,
        logo=media_url(b.logo) if b.logo else "",
        models=[TruckModelOut(id=m.id, name=m.name) for m in (b.models or []) if m.is_active],
    )


def serialize_category(
    c: Category, lang: str = "ru", children: list[Category] | None = None
) -> CategoryOut:
    return CategoryOut(
        id=c.id,
        name=c.name(lang),
        name_ru=c.name_ru,
        name_uz=c.name_uz,
        slug=c.slug,
        parent_id=c.parent_id,
        commission_override=_dec(c.commission_override)
        if c.commission_override is not None
        else None,
        sort_order=c.sort_order,
        is_active=c.is_active,
        children=[serialize_category(ch, lang) for ch in (children or [])],
    )


# ---- Seller ----
def serialize_seller_brief(sp: SellerProfile) -> SellerBrief:
    return SellerBrief(
        id=sp.id,
        shop_name=sp.shop_name,
        rating=_dec(sp.rating),
        reviews_count=sp.reviews_count,
        orders_count=sp.orders_count,
        completion_rate=_dec(sp.completion_rate),
    )


# ---- Products ----
def _primary_image(p: Product) -> str | None:
    if p.images:
        return media_url(p.images[0].path)
    return None


def serialize_product_list_item(p: Product, lang: str = "ru") -> ProductListItem:
    return ProductListItem(
        id=p.id,
        name=p.name(lang),
        article=p.article,
        oem_number=p.oem_number,
        part_brand=p.part_brand,
        price=_dec(p.price),
        currency=p.currency,
        stock_qty=p.stock_qty,
        in_stock=p.stock_qty > 0,
        image=_primary_image(p),
        category_id=p.category_id,
        seller=serialize_seller_brief(p.seller) if p.seller else None,
        status=p.status.value,
        bonus=_dec(p.bonus),
    )


def serialize_product(p: Product, lang: str = "ru") -> ProductOut:
    base = serialize_product_list_item(p, lang)
    return ProductOut(
        **base.model_dump(),
        name_ru=p.name_ru,
        name_uz=p.name_uz,
        description=p.description_uz if lang == "uz" and p.description_uz else p.description_ru,
        description_ru=p.description_ru,
        description_uz=p.description_uz,
        warranty=p.warranty,
        engine=p.engine,
        is_active=p.is_active,
        images=[
            ProductImageOut(id=img.id, url=media_url(img.path), sort_order=img.sort_order)
            for img in p.images
        ],
        vehicles=[
            VehicleOut(
                id=v.id,
                brand_id=v.truck_brand_id,
                brand_name=v.brand.name if v.brand else "",
                model_id=v.truck_model_id,
                model_name=v.model.name if v.model else None,
            )
            for v in p.vehicles
        ],
    )


# ---- Cart ----
def serialize_cart(cart: Cart, lang: str = "ru") -> CartOut:
    items: list[CartItemOut] = []
    subtotal = 0.0
    count = 0
    for it in cart.items:
        p = it.product
        if p is None:
            continue
        line = _dec(p.price) * it.quantity
        subtotal += line
        count += it.quantity
        items.append(
            CartItemOut(
                id=it.id,
                product_id=p.id,
                name=p.name(lang),
                article=p.article,
                price=_dec(p.price),
                quantity=it.quantity,
                line_total=line,
                image=_primary_image(p),
                stock_qty=p.stock_qty,
                seller_id=p.seller_id,
                seller_name=p.seller.shop_name if p.seller else "",
            )
        )
    return CartOut(id=cart.id, items=items, subtotal=subtotal, count=count)


# ---- Orders ----
def summarize_status(seller_orders: list[SellerOrder]) -> str:
    statuses = {so.status for so in seller_orders}
    if not statuses:
        return OrderStatus.new.value
    if len(statuses) == 1:
        return next(iter(statuses)).value
    if statuses <= {OrderStatus.completed, OrderStatus.cancelled}:
        return (
            OrderStatus.completed.value
            if OrderStatus.completed in statuses
            else OrderStatus.cancelled.value
        )
    return OrderStatus.processing.value


def _order_item_out(oi: OrderItem) -> OrderItemOut:
    image = None
    if oi.product and oi.product.images:
        image = media_url(oi.product.images[0].path)
    return OrderItemOut(
        id=oi.id,
        product_id=oi.product_id,
        product_name=oi.product_name,
        article=oi.article,
        unit_price=_dec(oi.unit_price),
        quantity=oi.quantity,
        line_total=_dec(oi.line_total),
        image=image,
    )


def serialize_seller_order(so: SellerOrder, is_buyer: bool = False) -> SellerOrderOut:
    reviewed = so.review is not None
    return SellerOrderOut(
        id=so.id,
        seller_id=so.seller_id,
        seller_name=so.seller.shop_name if so.seller else "",
        status=so.status.value,
        subtotal=_dec(so.subtotal),
        commission_amount=_dec(so.commission_amount),
        seller_payout=_dec(so.seller_payout),
        items=[_order_item_out(oi) for oi in so.items],
        can_review=is_buyer and so.status == OrderStatus.completed and not reviewed,
        reviewed=reviewed,
    )


def serialize_order(order: Order, is_buyer: bool = False) -> OrderOut:
    return OrderOut(
        id=order.id,
        status_summary=summarize_status(order.seller_orders),
        contact_name=order.contact_name,
        phone=order.phone,
        city=order.city,
        address=order.address,
        comment=order.comment,
        latitude=order.latitude,
        longitude=order.longitude,
        delivery_method=order.delivery_method.value,
        payment_method=order.payment_method.value,
        payment_status=order.payment_status.value,
        subtotal=_dec(order.subtotal),
        discount=_dec(order.discount),
        delivery_cost=_dec(order.delivery_cost),
        total=_dec(order.total),
        created_at=order.created_at.isoformat() if order.created_at else "",
        seller_orders=[serialize_seller_order(so, is_buyer) for so in order.seller_orders],
    )


def serialize_seller_order_row(so: SellerOrder) -> SellerOrderRow:
    order = so.order
    return SellerOrderRow(
        id=so.id,
        order_id=so.order_id,
        status=so.status.value,
        buyer_name=order.contact_name if order else "",
        phone=order.phone if order else "",
        city=order.city if order else "",
        address=order.address if order else "",
        comment=order.comment if order else "",
        latitude=order.latitude if order else None,
        longitude=order.longitude if order else None,
        delivery_method=order.delivery_method.value if order else "delivery",
        subtotal=_dec(so.subtotal),
        commission_amount=_dec(so.commission_amount),
        seller_payout=_dec(so.seller_payout),
        items=[_order_item_out(oi) for oi in so.items],
        created_at=so.created_at.isoformat() if so.created_at else "",
    )


def serialize_order_list_item(order: Order) -> OrderListItem:
    items_count = sum(len(so.items) for so in order.seller_orders)
    return OrderListItem(
        id=order.id,
        status_summary=summarize_status(order.seller_orders),
        total=_dec(order.total),
        payment_status=order.payment_status.value,
        items_count=items_count,
        created_at=order.created_at.isoformat() if order.created_at else "",
    )


# ---- Reviews / Messages / Banners ----
def serialize_review(r: Review) -> ReviewOut:
    return ReviewOut(
        id=r.id,
        seller_order_id=r.seller_order_id,
        seller_id=r.seller_id,
        stars=r.stars,
        comment=r.comment,
        created_at=r.created_at.isoformat() if r.created_at else "",
    )


def serialize_message(m: Message) -> MessageOut:
    return MessageOut(
        id=m.id,
        from_user_id=m.from_user_id,
        to_user_id=m.to_user_id,
        kind=m.kind.value,
        product_id=m.product_id,
        order_id=m.order_id,
        text=m.text,
        is_read=m.is_read,
        created_at=m.created_at.isoformat() if m.created_at else "",
    )


def serialize_banner(b: Banner) -> BannerOut:
    return BannerOut(
        id=b.id,
        title=b.title,
        image=media_url(b.image),
        target=b.target,
        is_active=b.is_active,
        sort_order=b.sort_order,
    )
