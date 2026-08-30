from __future__ import annotations

from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.serializers import serialize_brand, serialize_category
from app.core.deps import OptionalUser, SessionDep
from app.models.catalog import Category, TruckBrand, TruckModel
from app.schemas.catalog import CategoryOut, TruckBrandOut, TruckModelOut

router = APIRouter(tags=["catalog"])


def resolve_lang(user: OptionalUser, lang: str | None) -> str:
    if lang in ("ru", "uz"):
        return lang
    if user is not None:
        return user.language.value
    return "ru"


@router.get("/brands", response_model=list[TruckBrandOut])
async def list_brands(
    session: SessionDep,
    user: OptionalUser,
    lang: str | None = Query(default=None),
) -> list[TruckBrandOut]:
    result = await session.execute(
        select(TruckBrand)
        .where(TruckBrand.is_active.is_(True))
        .options(selectinload(TruckBrand.models))
        .order_by(TruckBrand.sort_order, TruckBrand.name)
    )
    return [serialize_brand(b) for b in result.scalars().unique().all()]


@router.get("/brands/{brand_id}/models", response_model=list[TruckModelOut])
async def list_models(brand_id: int, session: SessionDep) -> list[TruckModelOut]:
    result = await session.execute(
        select(TruckModel)
        .where(TruckModel.brand_id == brand_id, TruckModel.is_active.is_(True))
        .order_by(TruckModel.name)
    )
    return [TruckModelOut(id=m.id, name=m.name) for m in result.scalars().all()]


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(
    session: SessionDep,
    user: OptionalUser,
    lang: str | None = Query(default=None),
    tree: bool = Query(default=True),
) -> list[CategoryOut]:
    language = resolve_lang(user, lang)
    result = await session.execute(
        select(Category)
        .where(Category.is_active.is_(True))
        .order_by(Category.sort_order, Category.name_ru)
    )
    categories = list(result.scalars().all())

    if not tree:
        return [serialize_category(c, language) for c in categories]

    by_parent: dict[int | None, list[Category]] = {}
    for c in categories:
        by_parent.setdefault(c.parent_id, []).append(c)

    def build(c: Category) -> CategoryOut:
        out = serialize_category(c, language)
        out.children = [build(ch) for ch in by_parent.get(c.id, [])]
        return out

    return [build(c) for c in by_parent.get(None, [])]
