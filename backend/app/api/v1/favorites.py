from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.serializers import serialize_product_list_item, serialize_seller_brief
from app.api.v1.catalog import resolve_lang
from app.core.deps import CurrentUser, SessionDep
from app.models.favorite import FavoriteProduct, FavoriteSeller
from app.models.product import Product
from app.models.user import SellerProfile
from app.schemas.common import Msg
from app.schemas.misc import FavoriteProductIn, FavoriteSellerIn
from app.schemas.product import ProductListItem, SellerBrief

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("/products", response_model=list[ProductListItem])
async def list_fav_products(
    session: SessionDep, user: CurrentUser, lang: str | None = Query(default=None)
) -> list[ProductListItem]:
    result = await session.execute(
        select(Product)
        .join(FavoriteProduct, FavoriteProduct.product_id == Product.id)
        .where(FavoriteProduct.user_id == user.id)
        .options(selectinload(Product.images), selectinload(Product.seller))
        .order_by(FavoriteProduct.id.desc())
    )
    language = resolve_lang(user, lang)
    return [serialize_product_list_item(p, language) for p in result.scalars().unique().all()]


@router.post("/products", response_model=Msg)
async def add_fav_product(
    payload: FavoriteProductIn, session: SessionDep, user: CurrentUser
) -> Msg:
    exists = (
        await session.execute(
            select(FavoriteProduct).where(
                FavoriteProduct.user_id == user.id,
                FavoriteProduct.product_id == payload.product_id,
            )
        )
    ).scalar_one_or_none()
    if exists is None:
        session.add(FavoriteProduct(user_id=user.id, product_id=payload.product_id))
        await session.commit()
    return Msg(detail="added")


@router.delete("/products/{product_id}", response_model=Msg)
async def remove_fav_product(product_id: int, session: SessionDep, user: CurrentUser) -> Msg:
    fav = (
        await session.execute(
            select(FavoriteProduct).where(
                FavoriteProduct.user_id == user.id, FavoriteProduct.product_id == product_id
            )
        )
    ).scalar_one_or_none()
    if fav:
        await session.delete(fav)
        await session.commit()
    return Msg(detail="removed")


@router.get("/sellers", response_model=list[SellerBrief])
async def list_fav_sellers(session: SessionDep, user: CurrentUser) -> list[SellerBrief]:
    result = await session.execute(
        select(SellerProfile)
        .join(FavoriteSeller, FavoriteSeller.seller_id == SellerProfile.id)
        .where(FavoriteSeller.user_id == user.id)
        .order_by(FavoriteSeller.id.desc())
    )
    return [serialize_seller_brief(s) for s in result.scalars().all()]


@router.post("/sellers", response_model=Msg)
async def add_fav_seller(payload: FavoriteSellerIn, session: SessionDep, user: CurrentUser) -> Msg:
    exists = (
        await session.execute(
            select(FavoriteSeller).where(
                FavoriteSeller.user_id == user.id, FavoriteSeller.seller_id == payload.seller_id
            )
        )
    ).scalar_one_or_none()
    if exists is None:
        session.add(FavoriteSeller(user_id=user.id, seller_id=payload.seller_id))
        await session.commit()
    return Msg(detail="added")


@router.delete("/sellers/{seller_id}", response_model=Msg)
async def remove_fav_seller(seller_id: int, session: SessionDep, user: CurrentUser) -> Msg:
    fav = (
        await session.execute(
            select(FavoriteSeller).where(
                FavoriteSeller.user_id == user.id, FavoriteSeller.seller_id == seller_id
            )
        )
    ).scalar_one_or_none()
    if fav:
        await session.delete(fav)
        await session.commit()
    return Msg(detail="removed")
