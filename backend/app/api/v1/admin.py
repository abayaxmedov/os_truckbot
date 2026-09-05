from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.api.serializers import serialize_banner, serialize_product, serialize_product_list_item
from app.services.media import media_url
from app.core.deps import CurrentAdmin, SessionDep
from app.core.utils import normalize_part_number, slugify
from app.models.analog import AnalogGroup, AnalogReference
from app.models.banner import Banner
from app.models.catalog import Category
from app.models.enums import PayoutStatus, ProductStatus, SellerStatus
from app.models.master import MasterProfile, Payout
from app.models.product import Product, ProductVehicle
from app.models.setting import KEY_DEFAULT_COMMISSION, KEY_SUPPORT_TELEGRAM
from app.models.user import SellerProfile, User
from app.schemas.admin import (
    AdminMasterOut,
    AdminSellerOut,
    AdminStatsOut,
    AnalogGroupIn,
    AnalogGroupOut,
    AnalogNumberIn,
    AnalogReferenceOut,
    BannerIn,
    BannerOut,
    CategoryCreate,
    CategoryUpdate,
    CommissionUpdate,
    SupportTelegramUpdate,
    MasterVerifyUpdate,
    ProductModerate,
    SellerCommissionUpdate,
    SellerStatusUpdate,
)
from app.schemas.catalog import CategoryOut
from app.schemas.common import Msg, Page
from app.schemas.master import AdminPayoutOut, ProductBonusUpdate
from app.schemas.product import ProductListItem, ProductOut, ProductUpdate
from app.services.bonus import approve_payout, reject_payout, run_scheduled_payouts
from app.services.settings_service import all_settings, set_setting
from app.services.stats import get_admin_stats, get_popular_products

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[])


# ---- Dashboard ----
@router.get("/stats", response_model=AdminStatsOut)
async def admin_stats(session: SessionDep, admin: CurrentAdmin) -> AdminStatsOut:
    stats = await get_admin_stats(session)
    popular = await get_popular_products(session, limit=10)
    return AdminStatsOut(**stats, popular_products=popular)


# ---- Sellers ----
@router.get("/sellers", response_model=list[AdminSellerOut])
async def list_sellers(session: SessionDep, admin: CurrentAdmin) -> list[AdminSellerOut]:
    result = await session.execute(
        select(SellerProfile)
        .options(selectinload(SellerProfile.user))
        .order_by(SellerProfile.id.desc())
    )
    sellers = result.scalars().all()
    out: list[AdminSellerOut] = []
    for sp in sellers:
        products_count = (
            await session.execute(select(func.count(Product.id)).where(Product.seller_id == sp.id))
        ).scalar_one()
        out.append(
            AdminSellerOut(
                id=sp.id,
                user_id=sp.user_id,
                telegram_id=sp.user.telegram_id if sp.user else 0,
                shop_name=sp.shop_name,
                status=sp.status.value,
                rating=float(sp.rating or 0),
                orders_count=sp.orders_count,
                products_count=int(products_count),
                commission_override=float(sp.commission_override)
                if sp.commission_override is not None
                else None,
            )
        )
    return out


@router.patch("/sellers/{seller_id}/status", response_model=Msg)
async def set_seller_status(
    seller_id: int, payload: SellerStatusUpdate, session: SessionDep, admin: CurrentAdmin
) -> Msg:
    sp = await session.get(SellerProfile, seller_id)
    if sp is None:
        raise HTTPException(status_code=404, detail="seller_not_found")
    try:
        sp.status = SellerStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="bad_status") from exc
    await session.commit()
    return Msg(detail="updated")


@router.patch("/sellers/{seller_id}/commission", response_model=Msg)
async def set_seller_commission(
    seller_id: int, payload: SellerCommissionUpdate, session: SessionDep, admin: CurrentAdmin
) -> Msg:
    sp = await session.get(SellerProfile, seller_id)
    if sp is None:
        raise HTTPException(status_code=404, detail="seller_not_found")
    sp.commission_override = (
        Decimal(str(payload.commission_override))
        if payload.commission_override is not None
        else None
    )
    await session.commit()
    return Msg(detail="updated")


@router.delete("/sellers/{seller_id}", response_model=Msg)
async def delete_seller(seller_id: int, session: SessionDep, admin: CurrentAdmin) -> Msg:
    sp = await session.get(SellerProfile, seller_id)
    if sp is None:
        raise HTTPException(status_code=404, detail="seller_not_found")
    await session.delete(sp)
    await session.commit()
    return Msg(detail="deleted")


# ---- Product moderation ----
@router.get("/products", response_model=Page[ProductListItem])
async def admin_products(
    session: SessionDep,
    admin: CurrentAdmin,
    status: str | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> Page[ProductListItem]:
    filters = []
    if status:
        try:
            filters.append(Product.status == ProductStatus(status))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="bad_status") from exc
    if q:
        like = f"%{q}%"
        filters.append(
            (Product.name_ru.ilike(like))
            | (Product.article.ilike(like))
            | (Product.oem_number.ilike(like))
        )
    total = (await session.execute(select(func.count(Product.id)).where(*filters))).scalar_one()
    result = await session.execute(
        select(Product)
        .where(*filters)
        .options(selectinload(Product.images), selectinload(Product.seller))
        .order_by(Product.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    items = [serialize_product_list_item(p) for p in result.scalars().unique().all()]
    return Page[ProductListItem](items=items, total=int(total), page=page, page_size=page_size)


@router.patch("/products/{product_id}/moderate", response_model=Msg)
async def moderate_product(
    product_id: int, payload: ProductModerate, session: SessionDep, admin: CurrentAdmin
) -> Msg:
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product_not_found")
    try:
        product.status = ProductStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="bad_status") from exc
    await session.commit()
    return Msg(detail="moderated")


@router.patch("/products/{product_id}", response_model=ProductOut)
async def admin_edit_product(
    product_id: int, payload: ProductUpdate, session: SessionDep, admin: CurrentAdmin
) -> ProductOut:
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
    if product is None:
        raise HTTPException(status_code=404, detail="product_not_found")
    data = payload.model_dump(exclude_unset=True)
    data.pop("vehicles", None)
    for key, value in data.items():
        setattr(product, key, value)
    await session.commit()
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
    return serialize_product(result.scalar_one())


@router.delete("/products/{product_id}", response_model=Msg)
async def admin_delete_product(product_id: int, session: SessionDep, admin: CurrentAdmin) -> Msg:
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product_not_found")
    await session.delete(product)
    await session.commit()
    return Msg(detail="deleted")


# ---- Categories ----
@router.post("/categories", response_model=CategoryOut)
async def create_category(
    payload: CategoryCreate, session: SessionDep, admin: CurrentAdmin
) -> CategoryOut:
    slug = payload.slug or slugify(payload.name_ru)
    category = Category(
        name_ru=payload.name_ru,
        name_uz=payload.name_uz or payload.name_ru,
        slug=slug,
        parent_id=payload.parent_id,
        commission_override=Decimal(str(payload.commission_override))
        if payload.commission_override is not None
        else None,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
    )
    session.add(category)
    await session.commit()
    await session.refresh(category)
    from app.api.serializers import serialize_category

    return serialize_category(category)


@router.patch("/categories/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int, payload: CategoryUpdate, session: SessionDep, admin: CurrentAdmin
) -> CategoryOut:
    category = await session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="category_not_found")
    data = payload.model_dump(exclude_unset=True)
    if "commission_override" in data:
        val = data.pop("commission_override")
        category.commission_override = Decimal(str(val)) if val is not None else None
    for key, value in data.items():
        setattr(category, key, value)
    await session.commit()
    await session.refresh(category)
    from app.api.serializers import serialize_category

    return serialize_category(category)


@router.delete("/categories/{category_id}", response_model=Msg)
async def delete_category(category_id: int, session: SessionDep, admin: CurrentAdmin) -> Msg:
    category = await session.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="category_not_found")
    in_use = (
        await session.execute(
            select(func.count(Product.id)).where(Product.category_id == category_id)
        )
    ).scalar_one()
    if in_use:
        raise HTTPException(status_code=400, detail="category_in_use")
    await session.delete(category)
    await session.commit()
    return Msg(detail="deleted")


# ---- Settings / commission ----
@router.get("/settings", response_model=dict)
async def get_settings_map(session: SessionDep, admin: CurrentAdmin) -> dict:
    return await all_settings(session)


@router.patch("/settings/commission", response_model=Msg)
async def update_commission(
    payload: CommissionUpdate, session: SessionDep, admin: CurrentAdmin
) -> Msg:
    if payload.default_percent is not None:
        await set_setting(session, KEY_DEFAULT_COMMISSION, str(payload.default_percent))
        await session.commit()
    return Msg(detail="updated")


@router.patch("/settings/support", response_model=Msg)
async def update_support_telegram(
    payload: SupportTelegramUpdate, session: SessionDep, admin: CurrentAdmin
) -> Msg:
    # Store the handle without a leading '@' so the client can build t.me links cleanly.
    handle = payload.support_telegram.strip().lstrip("@")
    await set_setting(session, KEY_SUPPORT_TELEGRAM, handle)
    await session.commit()
    return Msg(detail="updated")


# ---- Banners ----
@router.get("/banners", response_model=list[BannerOut])
async def admin_banners(session: SessionDep, admin: CurrentAdmin) -> list[BannerOut]:
    result = await session.execute(select(Banner).order_by(Banner.sort_order, Banner.id))
    return [serialize_banner(b) for b in result.scalars().all()]


@router.post("/banners", response_model=BannerOut)
async def create_banner(payload: BannerIn, session: SessionDep, admin: CurrentAdmin) -> BannerOut:
    banner = Banner(
        title=payload.title,
        image=payload.image,
        target=payload.target,
        is_active=payload.is_active,
        sort_order=payload.sort_order,
    )
    session.add(banner)
    await session.commit()
    await session.refresh(banner)
    return serialize_banner(banner)


@router.patch("/banners/{banner_id}", response_model=BannerOut)
async def update_banner(
    banner_id: int, payload: BannerIn, session: SessionDep, admin: CurrentAdmin
) -> BannerOut:
    banner = await session.get(Banner, banner_id)
    if banner is None:
        raise HTTPException(status_code=404, detail="banner_not_found")
    banner.title = payload.title
    banner.image = payload.image
    banner.target = payload.target
    banner.is_active = payload.is_active
    banner.sort_order = payload.sort_order
    await session.commit()
    await session.refresh(banner)
    return serialize_banner(banner)


@router.delete("/banners/{banner_id}", response_model=Msg)
async def delete_banner(banner_id: int, session: SessionDep, admin: CurrentAdmin) -> Msg:
    banner = await session.get(Banner, banner_id)
    if banner is None:
        raise HTTPException(status_code=404, detail="banner_not_found")
    await session.delete(banner)
    await session.commit()
    return Msg(detail="deleted")


# ---- Analogs ----
def _serialize_group(group: AnalogGroup) -> AnalogGroupOut:
    return AnalogGroupOut(
        id=group.id,
        title=group.title,
        references=[
            AnalogReferenceOut(
                id=r.id,
                number=r.number,
                number_raw=r.number_raw,
                brand=r.brand,
                is_original=r.is_original,
            )
            for r in group.references
        ],
    )


@router.get("/analogs", response_model=list[AnalogGroupOut])
async def list_analogs(
    session: SessionDep,
    admin: CurrentAdmin,
    number: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AnalogGroupOut]:
    stmt = select(AnalogGroup).options(selectinload(AnalogGroup.references))
    if number:
        norm = normalize_part_number(number)
        group_ids = (
            select(AnalogReference.group_id).where(AnalogReference.number == norm).scalar_subquery()
        )
        stmt = stmt.where(AnalogGroup.id.in_(group_ids))
    stmt = stmt.order_by(AnalogGroup.id.desc()).limit(limit)
    result = await session.execute(stmt)
    return [_serialize_group(g) for g in result.scalars().unique().all()]


@router.post("/analogs", response_model=AnalogGroupOut)
async def create_analog_group(
    payload: AnalogGroupIn, session: SessionDep, admin: CurrentAdmin
) -> AnalogGroupOut:
    group = AnalogGroup(title=payload.title)
    session.add(group)
    await session.flush()
    for num in payload.numbers:
        session.add(
            AnalogReference(
                group_id=group.id,
                number=normalize_part_number(num.number),
                number_raw=num.number,
                brand=num.brand,
                is_original=num.is_original,
            )
        )
    await session.commit()
    result = await session.execute(
        select(AnalogGroup)
        .where(AnalogGroup.id == group.id)
        .options(selectinload(AnalogGroup.references))
    )
    return _serialize_group(result.scalar_one())


@router.post("/analogs/{group_id}/numbers", response_model=AnalogGroupOut)
async def add_analog_number(
    group_id: int, payload: AnalogNumberIn, session: SessionDep, admin: CurrentAdmin
) -> AnalogGroupOut:
    group = await session.get(AnalogGroup, group_id)
    if group is None:
        raise HTTPException(status_code=404, detail="group_not_found")
    session.add(
        AnalogReference(
            group_id=group_id,
            number=normalize_part_number(payload.number),
            number_raw=payload.number,
            brand=payload.brand,
            is_original=payload.is_original,
        )
    )
    await session.commit()
    result = await session.execute(
        select(AnalogGroup)
        .where(AnalogGroup.id == group_id)
        .options(selectinload(AnalogGroup.references))
    )
    return _serialize_group(result.scalar_one())


@router.delete("/analogs/references/{reference_id}", response_model=Msg)
async def delete_analog_reference(
    reference_id: int, session: SessionDep, admin: CurrentAdmin
) -> Msg:
    ref = await session.get(AnalogReference, reference_id)
    if ref is None:
        raise HTTPException(status_code=404, detail="reference_not_found")
    await session.delete(ref)
    await session.commit()
    return Msg(detail="deleted")


# ---- Master bonuses & payouts ----
@router.patch("/products/{product_id}/bonus", response_model=Msg)
async def set_product_bonus(
    product_id: int, payload: ProductBonusUpdate, session: SessionDep, admin: CurrentAdmin
) -> Msg:
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="product_not_found")
    product.bonus = Decimal(str(payload.bonus))
    await session.commit()
    return Msg(detail="updated")


@router.get("/payouts", response_model=list[AdminPayoutOut])
async def list_payouts(
    session: SessionDep,
    admin: CurrentAdmin,
    status: str | None = Query(default=None),
) -> list[AdminPayoutOut]:
    stmt = (
        select(Payout, User)
        .join(MasterProfile, MasterProfile.id == Payout.master_id)
        .join(User, User.id == MasterProfile.user_id)
        .order_by(Payout.id.desc())
    )
    if status:
        try:
            stmt = stmt.where(Payout.status == PayoutStatus(status))
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="bad_status") from exc
    result = await session.execute(stmt)
    out: list[AdminPayoutOut] = []
    for payout, user in result.all():
        out.append(
            AdminPayoutOut(
                id=payout.id,
                master_id=payout.master_id,
                master_name=user.full_name or user.username or str(user.telegram_id),
                phone=user.phone or "",
                amount=float(payout.amount),
                card_number=payout.card_number,
                status=payout.status.value,
                created_at=payout.created_at.isoformat() if payout.created_at else "",
            )
        )
    return out


@router.patch("/payouts/{payout_id}", response_model=Msg)
async def update_payout(
    payout_id: int,
    session: SessionDep,
    admin: CurrentAdmin,
    action: str = Query(...),  # "paid" | "rejected"
) -> Msg:
    payout = await session.get(Payout, payout_id)
    if payout is None:
        raise HTTPException(status_code=404, detail="payout_not_found")
    if action == "paid":
        await approve_payout(session, payout)
    elif action == "rejected":
        await reject_payout(session, payout)
    else:
        raise HTTPException(status_code=400, detail="bad_action")
    await session.commit()
    return Msg(detail="updated")


@router.post("/payouts/run", response_model=Msg)
async def run_payouts(session: SessionDep, admin: CurrentAdmin) -> Msg:
    """Manually trigger the 12-day payout cycle (also runs automatically in the background)."""
    count = await run_scheduled_payouts(session)
    await session.commit()
    return Msg(detail=f"created:{count}")


# ---- Masters (verification) ----
def _split_csv(csv: str) -> list[str]:
    return [c for c in (csv or "").split(",") if c]


@router.get("/masters", response_model=list[AdminMasterOut])
async def list_masters(session: SessionDep, admin: CurrentAdmin) -> list[AdminMasterOut]:
    result = await session.execute(
        select(MasterProfile)
        .options(selectinload(MasterProfile.user))
        .order_by(MasterProfile.is_verified.asc(), MasterProfile.id.desc())
    )
    out: list[AdminMasterOut] = []
    for mp in result.scalars().unique().all():
        u = mp.user
        name = " ".join(filter(None, [u.first_name if u else "", (u.last_name or "") if u else ""])).strip()
        out.append(
            AdminMasterOut(
                id=mp.id,
                user_id=mp.user_id,
                telegram_id=u.telegram_id if u else 0,
                name=name,
                phone=(u.phone or "") if u else "",
                photo=media_url(mp.photo),
                status=mp.status.value,
                is_verified=mp.is_verified,
                trucks=_split_csv(mp.trucks),
                specializations=_split_csv(mp.specializations),
                regions=mp.regions,
                experience_years=mp.experience_years,
            )
        )
    return out


@router.patch("/masters/{master_id}/verify", response_model=Msg)
async def set_master_verified(
    master_id: int, payload: MasterVerifyUpdate, session: SessionDep, admin: CurrentAdmin
) -> Msg:
    mp = await session.get(MasterProfile, master_id)
    if mp is None:
        raise HTTPException(status_code=404, detail="master_not_found")
    mp.is_verified = payload.is_verified
    await session.commit()
    return Msg(detail="updated")
