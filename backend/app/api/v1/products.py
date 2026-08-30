from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import selectinload

from app.api.serializers import serialize_product, serialize_product_list_item
from app.api.v1.catalog import resolve_lang
from app.core.deps import OptionalUser, SessionDep
from app.core.utils import normalize_part_number
from app.models.analog import AnalogReference
from app.models.catalog import Category
from app.models.enums import ProductStatus
from app.models.product import Product, ProductVehicle
from app.schemas.common import Page
from app.schemas.product import ProductListItem, ProductOut
from app.services.analogs import find_analog_products

router = APIRouter(prefix="/products", tags=["products"])

SORTS = {
    "new": Product.id.desc(),
    "price_asc": Product.price.asc(),
    "price_desc": Product.price.desc(),
    "popular": Product.views.desc(),
}


async def _child_category_ids(session: SessionDep, category_id: int) -> list[int]:
    result = await session.execute(
        select(Category.id).where(
            or_(Category.id == category_id, Category.parent_id == category_id)
        )
    )
    return [row[0] for row in result.all()]


def _search_condition(q: str):
    like = f"%{q.strip()}%"
    norm = normalize_part_number(q)
    conditions = [
        Product.name_ru.ilike(like),
        Product.name_uz.ilike(like),
        Product.article.ilike(like),
        Product.oem_number.ilike(like),
        Product.part_brand.ilike(like),
    ]
    if norm:
        group_ids = (
            select(AnalogReference.group_id).where(AnalogReference.number == norm).scalar_subquery()
        )
        numbers = (
            select(AnalogReference.number)
            .where(AnalogReference.group_id.in_(group_ids))
            .scalar_subquery()
        )
        conditions += [
            Product.article_norm == norm,
            Product.oem_norm == norm,
            Product.article_norm.in_(numbers),
            Product.oem_norm.in_(numbers),
        ]
    return or_(*conditions)


async def _build_filters(
    session: SessionDep,
    q: str | None,
    category_id: int | None,
    brand_id: int | None,
    model_id: int | None,
    engine: str | None,
    seller_id: int | None,
    min_price: float | None,
    max_price: float | None,
    only_approved: bool = True,
) -> list:
    filters = [Product.is_active.is_(True)]
    if only_approved:
        filters.append(Product.status == ProductStatus.approved)
    if q:
        filters.append(_search_condition(q))
    if category_id:
        ids = await _child_category_ids(session, category_id)
        filters.append(Product.category_id.in_(ids))
    if brand_id or model_id:
        veh = select(ProductVehicle.product_id)
        if brand_id:
            veh = veh.where(ProductVehicle.truck_brand_id == brand_id)
        if model_id:
            veh = veh.where(ProductVehicle.truck_model_id == model_id)
        filters.append(Product.id.in_(veh.scalar_subquery()))
    if engine:
        filters.append(Product.engine.ilike(f"%{engine}%"))
    if seller_id:
        filters.append(Product.seller_id == seller_id)
    if min_price is not None:
        filters.append(Product.price >= min_price)
    if max_price is not None:
        filters.append(Product.price <= max_price)
    return filters


@router.get("", response_model=Page[ProductListItem])
async def list_products(
    session: SessionDep,
    user: OptionalUser,
    q: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    brand_id: int | None = Query(default=None),
    model_id: int | None = Query(default=None),
    engine: str | None = Query(default=None),
    seller_id: int | None = Query(default=None),
    min_price: float | None = Query(default=None),
    max_price: float | None = Query(default=None),
    sort: str = Query(default="new"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    lang: str | None = Query(default=None),
) -> Page[ProductListItem]:
    language = resolve_lang(user, lang)
    filters = await _build_filters(
        session, q, category_id, brand_id, model_id, engine, seller_id, min_price, max_price
    )

    total = (
        await session.execute(select(func.count(Product.id)).where(and_(*filters)))
    ).scalar_one()

    order_by = SORTS.get(sort, Product.id.desc())
    stmt: Select = (
        select(Product)
        .where(and_(*filters))
        .options(selectinload(Product.images), selectinload(Product.seller))
        .order_by(order_by)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await session.execute(stmt)
    items = [serialize_product_list_item(p, language) for p in result.scalars().unique().all()]
    return Page[ProductListItem](items=items, total=int(total), page=page, page_size=page_size)


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: int,
    session: SessionDep,
    user: OptionalUser,
    lang: str | None = Query(default=None),
) -> ProductOut:
    language = resolve_lang(user, lang)
    result = await session.execute(
        select(Product)
        .where(Product.id == product_id)
        .options(
            selectinload(Product.images),
            selectinload(Product.seller),
            selectinload(Product.vehicles).selectinload(ProductVehicle.brand),
            selectinload(Product.vehicles).selectinload(ProductVehicle.model),
        )
    )
    product = result.scalar_one_or_none()
    if product is None or not product.is_active:
        raise HTTPException(status_code=404, detail="product_not_found")

    product.views += 1
    await session.commit()
    return serialize_product(product, language)


@router.get("/{product_id}/analogs", response_model=list[ProductListItem])
async def get_product_analogs(
    product_id: int,
    session: SessionDep,
    user: OptionalUser,
    lang: str | None = Query(default=None),
) -> list[ProductListItem]:
    language = resolve_lang(user, lang)
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product_not_found")
    number = product.oem_number or product.article
    products = await find_analog_products(session, number, exclude_product_id=product_id)
    return [serialize_product_list_item(p, language) for p in products]
