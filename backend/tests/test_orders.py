from __future__ import annotations

from decimal import Decimal

import pytest

from app.models.cart import Cart, CartItem
from app.models.catalog import Category
from app.models.enums import OrderStatus
from app.models.product import Product
from app.models.user import SellerProfile, User
from app.services.analogs import find_analog_products
from app.services.orders import CheckoutInput, OrderError, create_order


async def _make_seller(session, tg_id: int, shop: str) -> SellerProfile:
    user = User(telegram_id=tg_id, first_name=shop)
    session.add(user)
    await session.flush()
    sp = SellerProfile(user_id=user.id, shop_name=shop)
    session.add(sp)
    await session.flush()
    return sp


async def _make_product(session, seller, category, **kw) -> Product:
    p = Product(
        seller_id=seller.id,
        category_id=category.id,
        name_ru=kw.get("name", "Part"),
        **{k: v for k, v in kw.items() if k != "name"},
    )
    session.add(p)
    await session.flush()
    return p


@pytest.mark.asyncio
async def test_create_order_splits_and_commission(session):
    cat = Category(name_ru="Фильтры", name_uz="Filtr", slug="filtry")
    session.add(cat)
    await session.flush()

    seller = await _make_seller(session, 1001, "Shop A")
    product = await _make_product(
        session, seller, cat, name="Фильтр", price=Decimal("150000"), stock_qty=10, article="W1170"
    )

    buyer = User(telegram_id=2001, first_name="Buyer")
    session.add(buyer)
    await session.flush()

    cart = Cart(user_id=buyer.id)
    session.add(cart)
    await session.flush()
    session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=2))
    await session.flush()

    order = await create_order(
        session, buyer, CheckoutInput(contact_name="Buyer", phone="+998900000000")
    )
    await session.flush()

    assert order.total == Decimal("300000.00")
    assert len(order.seller_orders) == 1
    so = order.seller_orders[0]
    assert so.subtotal == Decimal("300000.00")
    assert so.commission_amount == Decimal("21000.00")  # 7% default
    assert so.seller_payout == Decimal("279000.00")
    assert so.status == OrderStatus.new
    # stock decremented, cart cleared
    assert product.stock_qty == 8


@pytest.mark.asyncio
async def test_checkout_empty_cart_raises(session):
    buyer = User(telegram_id=3001, first_name="Buyer")
    session.add(buyer)
    await session.flush()
    with pytest.raises(OrderError):
        await create_order(session, buyer, CheckoutInput(contact_name="B", phone="1"))


@pytest.mark.asyncio
async def test_out_of_stock_raises(session):
    cat = Category(name_ru="C", name_uz="C", slug="c")
    session.add(cat)
    await session.flush()
    seller = await _make_seller(session, 1002, "Shop B")
    product = await _make_product(session, seller, cat, price=Decimal("1000"), stock_qty=1)
    buyer = User(telegram_id=4001, first_name="Buyer")
    session.add(buyer)
    await session.flush()
    cart = Cart(user_id=buyer.id)
    session.add(cart)
    await session.flush()
    session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=5))
    await session.flush()
    with pytest.raises(OrderError):
        await create_order(session, buyer, CheckoutInput(contact_name="B", phone="1"))


@pytest.mark.asyncio
async def test_analog_search(session):
    from app.core.utils import normalize_part_number
    from app.models.analog import AnalogGroup, AnalogReference

    cat = Category(name_ru="Фильтры", name_uz="F", slug="filtry")
    session.add(cat)
    await session.flush()
    seller = await _make_seller(session, 1003, "Shop C")

    # Two products cross-referenced by the same OEM
    await _make_product(
        session,
        seller,
        cat,
        name="MANN",
        price=Decimal("1"),
        stock_qty=5,
        article="W1170",
        oem_number="51.10100-6126",
    )
    await _make_product(
        session,
        seller,
        cat,
        name="Bosch",
        price=Decimal("1"),
        stock_qty=5,
        article="P7131",
        oem_number="51.10100-6126",
    )

    grp = AnalogGroup(title="MAN filter")
    session.add(grp)
    await session.flush()
    for num, brand, orig in [
        ("51.10100-6126", "MAN", True),
        ("W1170", "MANN", False),
        ("P7131", "Bosch", False),
    ]:
        session.add(
            AnalogReference(
                group_id=grp.id,
                number=normalize_part_number(num),
                number_raw=num,
                brand=brand,
                is_original=orig,
            )
        )
    await session.flush()

    results = await find_analog_products(session, "51.10100-6126")
    names = sorted(p.name_ru for p in results)
    assert names == ["Bosch", "MANN"]
