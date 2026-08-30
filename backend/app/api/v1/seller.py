from __future__ import annotations

import logging

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.serializers import (
    serialize_product,
    serialize_product_list_item,
    serialize_seller_order_row,
)
from app.api.v1.catalog import resolve_lang
from app.core.deps import CurrentSeller, CurrentUser, SessionDep
from app.models.enums import OrderStatus, SellerStatus
from app.models.order import OrderItem, SellerOrder
from app.models.product import Product, ProductImage, ProductVehicle
from app.models.user import SellerProfile
from app.schemas.common import Msg, Page
from app.schemas.order import SellerOrderRow
from app.schemas.product import ProductCreate, ProductListItem, ProductOut, ProductUpdate
from app.schemas.seller import ImportResult, SellerOut, SellerRegister, SellerStatsOut
from app.services import notifications
from app.services.excel_import import build_template_xlsx, import_products
from app.services.media import MediaError, save_image
from app.services.orders import update_seller_order_status
from app.services.stats import get_seller_stats

router = APIRouter(prefix="/seller", tags=["seller"])
logger = logging.getLogger(__name__)

_PRODUCT_LOAD = (
    selectinload(Product.images),
    selectinload(Product.seller),
    selectinload(Product.vehicles).selectinload(ProductVehicle.brand),
    selectinload(Product.vehicles).selectinload(ProductVehicle.model),
)


def seller_to_out(sp: SellerProfile) -> SellerOut:
    return SellerOut(
        id=sp.id,
        user_id=sp.user_id,
        shop_name=sp.shop_name,
        description=sp.description,
        status=sp.status.value,
        rating=float(sp.rating or 0),
        orders_count=sp.orders_count,
        reviews_count=sp.reviews_count,
        completion_rate=float(sp.completion_rate or 0),
        commission_override=float(sp.commission_override)
        if sp.commission_override is not None
        else None,
    )


@router.post("/register", response_model=SellerOut)
async def register_seller(
    payload: SellerRegister, session: SessionDep, user: CurrentUser
) -> SellerOut:
    if user.seller_profile is not None:
        raise HTTPException(status_code=400, detail="already_seller")
    sp = SellerProfile(
        user_id=user.id,
        shop_name=payload.shop_name,
        description=payload.description,
        status=SellerStatus.active,
    )
    session.add(sp)
    await session.commit()
    await session.refresh(sp)
    try:
        await notifications.notify_new_seller(session, sp.id)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to notify admins about new seller %s", sp.id)
    return seller_to_out(sp)


@router.get("", response_model=SellerOut)
async def my_seller(seller: CurrentSeller) -> SellerOut:
    return seller_to_out(seller)


@router.get("/stats", response_model=SellerStatsOut)
async def seller_stats(session: SessionDep, seller: CurrentSeller) -> SellerStatsOut:
    stats = await get_seller_stats(session, seller.id)
    return SellerStatsOut(
        **stats,
        rating=float(seller.rating or 0),
        reviews_count=seller.reviews_count,
        completion_rate=float(seller.completion_rate or 0),
    )


# ---- Products ----
@router.get("/products", response_model=Page[ProductListItem])
async def my_products(
    session: SessionDep,
    seller: CurrentSeller,
    user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    lang: str | None = Query(default=None),
) -> Page[ProductListItem]:
    total = (
        await session.execute(select(func.count(Product.id)).where(Product.seller_id == seller.id))
    ).scalar_one()
    result = await session.execute(
        select(Product)
        .where(Product.seller_id == seller.id)
        .options(selectinload(Product.images), selectinload(Product.seller))
        .order_by(Product.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    language = resolve_lang(user, lang)
    items = [serialize_product_list_item(p, language) for p in result.scalars().unique().all()]
    return Page[ProductListItem](items=items, total=int(total), page=page, page_size=page_size)


async def _get_owned_product(session, seller_id: int, product_id: int) -> Product:
    result = await session.execute(
        select(Product).where(Product.id == product_id).options(*_PRODUCT_LOAD)
    )
    product = result.scalar_one_or_none()
    if product is None or product.seller_id != seller_id:
        raise HTTPException(status_code=404, detail="product_not_found")
    return product


@router.post("/products", response_model=ProductOut)
async def create_product(
    payload: ProductCreate, session: SessionDep, seller: CurrentSeller
) -> ProductOut:
    product = Product(
        seller_id=seller.id,
        category_id=payload.category_id,
        name_ru=payload.name_ru,
        name_uz=payload.name_uz,
        article=payload.article,
        oem_number=payload.oem_number,
        part_brand=payload.part_brand,
        engine=payload.engine,
        description_ru=payload.description_ru,
        description_uz=payload.description_uz,
        price=payload.price,
        stock_qty=payload.stock_qty,
        warranty=payload.warranty,
    )
    session.add(product)
    await session.flush()
    for v in payload.vehicles:
        session.add(
            ProductVehicle(
                product_id=product.id,
                truck_brand_id=v.truck_brand_id,
                truck_model_id=v.truck_model_id,
            )
        )
    await session.commit()
    product = await _get_owned_product(session, seller.id, product.id)
    return serialize_product(product)


@router.patch("/products/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int, payload: ProductUpdate, session: SessionDep, seller: CurrentSeller
) -> ProductOut:
    product = await _get_owned_product(session, seller.id, product_id)
    data = payload.model_dump(exclude_unset=True)
    vehicles = data.pop("vehicles", None)
    for key, value in data.items():
        setattr(product, key, value)
    if vehicles is not None:
        for v in list(product.vehicles):
            await session.delete(v)
        await session.flush()
        for v in vehicles:
            session.add(
                ProductVehicle(
                    product_id=product.id,
                    truck_brand_id=v["truck_brand_id"],
                    truck_model_id=v.get("truck_model_id"),
                )
            )
    await session.commit()
    product = await _get_owned_product(session, seller.id, product_id)
    return serialize_product(product)


@router.delete("/products/{product_id}", response_model=Msg)
async def delete_product(product_id: int, session: SessionDep, seller: CurrentSeller) -> Msg:
    product = await _get_owned_product(session, seller.id, product_id)
    await session.delete(product)
    await session.commit()
    return Msg(detail="deleted")


@router.post("/products/{product_id}/images", response_model=ProductOut)
async def upload_product_image(
    product_id: int,
    session: SessionDep,
    seller: CurrentSeller,
    file: UploadFile = File(...),
) -> ProductOut:
    product = await _get_owned_product(session, seller.id, product_id)
    try:
        path = await save_image(file, subdir="products")
    except MediaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    next_order = max((img.sort_order for img in product.images), default=-1) + 1
    session.add(ProductImage(product_id=product.id, path=path, sort_order=next_order))
    await session.commit()
    product = await _get_owned_product(session, seller.id, product_id)
    return serialize_product(product)


# ---- Bulk import ----
@router.get("/products/import/template")
async def import_template() -> Response:
    data = build_template_xlsx()
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=products_template.xlsx"},
    )


@router.post("/products/import", response_model=ImportResult)
async def import_bulk(
    session: SessionDep, seller: CurrentSeller, file: UploadFile = File(...)
) -> ImportResult:
    data = await file.read()
    result = await import_products(session, seller.id, data, file.filename or "products.xlsx")
    await session.commit()
    return ImportResult(**result)


# ---- Orders ----
@router.get("/orders", response_model=list[SellerOrderRow])
async def seller_orders(
    session: SessionDep,
    seller: CurrentSeller,
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[SellerOrderRow]:
    stmt = (
        select(SellerOrder)
        .where(SellerOrder.seller_id == seller.id)
        .options(
            selectinload(SellerOrder.order),
            selectinload(SellerOrder.items)
            .selectinload(OrderItem.product)
            .selectinload(Product.images),
        )
        .order_by(SellerOrder.id.desc())
    )
    if status_filter:
        try:
            stmt = stmt.where(SellerOrder.status == OrderStatus(status_filter))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="bad_status") from exc
    result = await session.execute(stmt)
    return [serialize_seller_order_row(so) for so in result.scalars().unique().all()]


@router.patch("/orders/{seller_order_id}/status", response_model=Msg)
async def update_order_status(
    seller_order_id: int,
    session: SessionDep,
    seller: CurrentSeller,
    status: str = Query(...),
) -> Msg:
    try:
        new_status = OrderStatus(status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="bad_status") from exc
    so = await session.get(SellerOrder, seller_order_id)
    if so is None or so.seller_id != seller.id:
        raise HTTPException(status_code=404, detail="order_not_found")
    await update_seller_order_status(session, so, new_status)
    await session.commit()
    try:
        await notifications.notify_status_change(session, so.id)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to notify buyer about status change %s", so.id)
    return Msg(detail="updated")
