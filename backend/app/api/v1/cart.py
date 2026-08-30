from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.serializers import serialize_cart
from app.api.v1.catalog import resolve_lang
from app.core.deps import CurrentUser, SessionDep
from app.models.cart import Cart, CartItem
from app.models.enums import ProductStatus
from app.models.product import Product
from app.schemas.cart import CartItemIn, CartItemUpdate, CartOut
from app.schemas.common import Msg
from app.services.orders import get_or_create_cart

router = APIRouter(prefix="/cart", tags=["cart"])


async def _load_cart(session: SessionDep, user_id: int) -> Cart:
    await get_or_create_cart(session, user_id)
    result = await session.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.images),
            selectinload(Cart.items).selectinload(CartItem.product).selectinload(Product.seller),
        )
    )
    return result.scalar_one()


@router.get("", response_model=CartOut)
async def get_cart(
    session: SessionDep, user: CurrentUser, lang: str | None = Query(default=None)
) -> CartOut:
    cart = await _load_cart(session, user.id)
    return serialize_cart(cart, resolve_lang(user, lang))


@router.post("/items", response_model=CartOut)
async def add_item(
    payload: CartItemIn,
    session: SessionDep,
    user: CurrentUser,
    lang: str | None = Query(default=None),
) -> CartOut:
    product = await session.get(Product, payload.product_id)
    if product is None or not product.is_active or product.status != ProductStatus.approved:
        raise HTTPException(status_code=404, detail="product_unavailable")

    cart = await get_or_create_cart(session, user.id)
    existing = (
        await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id, CartItem.product_id == product.id)
        )
    ).scalar_one_or_none()

    new_qty = (existing.quantity if existing else 0) + payload.quantity
    if new_qty > product.stock_qty:
        new_qty = product.stock_qty
    if new_qty < 1:
        raise HTTPException(status_code=400, detail="out_of_stock")

    if existing:
        existing.quantity = new_qty
    else:
        session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=new_qty))
    await session.commit()

    cart = await _load_cart(session, user.id)
    return serialize_cart(cart, resolve_lang(user, lang))


@router.patch("/items/{item_id}", response_model=CartOut)
async def update_item(
    item_id: int,
    payload: CartItemUpdate,
    session: SessionDep,
    user: CurrentUser,
    lang: str | None = Query(default=None),
) -> CartOut:
    item = await session.get(
        CartItem, item_id, options=[selectinload(CartItem.cart), selectinload(CartItem.product)]
    )
    if item is None or item.cart.user_id != user.id:
        raise HTTPException(status_code=404, detail="item_not_found")
    qty = min(payload.quantity, item.product.stock_qty) if item.product else payload.quantity
    if qty < 1:
        raise HTTPException(status_code=400, detail="out_of_stock")
    item.quantity = qty
    await session.commit()
    cart = await _load_cart(session, user.id)
    return serialize_cart(cart, resolve_lang(user, lang))


@router.delete("/items/{item_id}", response_model=CartOut)
async def delete_item(
    item_id: int, session: SessionDep, user: CurrentUser, lang: str | None = Query(default=None)
) -> CartOut:
    item = await session.get(CartItem, item_id, options=[selectinload(CartItem.cart)])
    if item is None or item.cart.user_id != user.id:
        raise HTTPException(status_code=404, detail="item_not_found")
    await session.delete(item)
    await session.commit()
    cart = await _load_cart(session, user.id)
    return serialize_cart(cart, resolve_lang(user, lang))


@router.delete("", response_model=Msg)
async def clear_cart(session: SessionDep, user: CurrentUser) -> Msg:
    cart = await get_or_create_cart(session, user.id)
    for item in list(cart.items):
        await session.delete(item)
    await session.commit()
    return Msg(detail="cleared")
