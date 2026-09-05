from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.serializers import serialize_banner, serialize_product_list_item
from app.api.v1.catalog import resolve_lang
from app.core.deps import OptionalUser, SessionDep
from app.models.banner import Banner
from app.models.enums import ProductStatus
from app.models.product import Product
from app.schemas.admin import BannerOut
from app.schemas.product import ProductListItem
from app.services.settings_service import get_support_telegram

router = APIRouter(tags=["public"])


@router.get("/settings", response_model=dict)
async def public_settings(session: SessionDep) -> dict:
    """Client-visible settings (no auth). Currently the support/admin Telegram handle."""
    return {"support_telegram": await get_support_telegram(session)}


@router.get("/banners", response_model=list[BannerOut])
async def active_banners(session: SessionDep) -> list[BannerOut]:
    result = await session.execute(
        select(Banner).where(Banner.is_active.is_(True)).order_by(Banner.sort_order, Banner.id)
    )
    return [serialize_banner(b) for b in result.scalars().all()]


@router.get("/popular", response_model=list[ProductListItem])
async def popular_products(
    session: SessionDep,
    user: OptionalUser,
    limit: int = Query(default=10, ge=1, le=50),
    lang: str | None = Query(default=None),
) -> list[ProductListItem]:
    result = await session.execute(
        select(Product)
        .where(Product.is_active.is_(True), Product.status == ProductStatus.approved)
        .options(selectinload(Product.images), selectinload(Product.seller))
        .order_by(Product.views.desc(), Product.id.desc())
        .limit(limit)
    )
    language = resolve_lang(user, lang)
    return [serialize_product_list_item(p, language) for p in result.scalars().unique().all()]
