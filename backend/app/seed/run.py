from __future__ import annotations

import asyncio
import logging
import shutil
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.utils import normalize_part_number
from app.db.session import SessionLocal
from app.models.analog import AnalogGroup, AnalogReference
from app.models.catalog import Category, TruckBrand
from app.models.enums import Language, ProductStatus, SellerStatus
from app.models.product import Product, ProductImage, ProductVehicle
from app.models.setting import KEY_DEFAULT_COMMISSION, Setting
from app.models.user import SellerProfile, User
from app.seed import data
from app.services.media import MEDIA_ROOT

# Demo product article -> generated illustration file (see app/seed/gen_images.py)
PRODUCT_IMAGE_BY_ARTICLE = {
    "W1170": "oil-filter.svg",
    "P7131": "oil-filter-b.svg",
    "FF5320": "fuel-filter.svg",
    "29202": "brake-pads.svg",
    "BD1567": "brake-disc.svg",
    "51039010217": "gasket.svg",
    "4157N1": "air-spring.svg",
    "SA080": "shock.svg",
    "0001241014": "starter.svg",
    "OIL1040": "oil-canister.svg",
    "6PK1801": "belt.svg",
    "VKBA5423": "bearing.svg",
}
_IMAGES_SRC = Path(__file__).resolve().parent / "images"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")


async def seed_brands(session) -> dict[str, TruckBrand]:
    existing = {b.slug: b for b in (await session.execute(select(TruckBrand))).scalars().all()}
    for order, (name, slug) in enumerate(data.TRUCK_BRANDS):
        if slug not in existing:
            brand = TruckBrand(name=name, slug=slug, sort_order=order)
            session.add(brand)
            existing[slug] = brand
    await session.flush()
    return existing


async def seed_categories(session) -> dict[str, Category]:
    existing = {c.slug: c for c in (await session.execute(select(Category))).scalars().all()}
    for order, (name_ru, name_uz, slug) in enumerate(data.CATEGORIES):
        if slug not in existing:
            cat = Category(name_ru=name_ru, name_uz=name_uz, slug=slug, sort_order=order)
            session.add(cat)
            existing[slug] = cat
    await session.flush()
    return existing


async def seed_settings(session) -> None:
    row = await session.get(Setting, KEY_DEFAULT_COMMISSION)
    if row is None:
        session.add(
            Setting(
                key=KEY_DEFAULT_COMMISSION,
                value=str(settings.default_commission_percent),
            )
        )
    await session.flush()


async def _get_or_create_user(session, tg_id: int, first_name: str, is_admin: bool = False) -> User:
    user = (
        await session.execute(select(User).where(User.telegram_id == tg_id))
    ).scalar_one_or_none()
    if user is None:
        user = User(
            telegram_id=tg_id,
            first_name=first_name,
            username=f"demo{tg_id}",
            language=Language.ru,
            is_admin=is_admin,
            onboarded=True,  # demo users are pre-onboarded
        )
        session.add(user)
        await session.flush()
    return user


async def seed_users(session) -> dict[str, SellerProfile]:
    # Admin(s): configured admin ids + a dev admin for DEV_AUTH_BYPASS
    for admin_id in settings.admin_ids:
        await _get_or_create_user(session, admin_id, "Admin", is_admin=True)
    await _get_or_create_user(session, data.DEV_ADMIN_TG, "Demo Admin", is_admin=True)
    await _get_or_create_user(session, data.DEV_BUYER_TG, "Demo Buyer")

    sellers: dict[str, SellerProfile] = {}
    for tg_id, shop in (
        (data.DEV_SELLER1_TG, "AutoParts UZ"),
        (data.DEV_SELLER2_TG, "TruckMaster"),
    ):
        user = await _get_or_create_user(session, tg_id, shop)
        sp = (
            await session.execute(select(SellerProfile).where(SellerProfile.user_id == user.id))
        ).scalar_one_or_none()
        if sp is None:
            sp = SellerProfile(
                user_id=user.id,
                shop_name=shop,
                description=f"{shop} — запчасти для грузовиков",
                status=SellerStatus.active,
            )
            session.add(sp)
            await session.flush()
        sellers[shop] = sp
    return sellers


async def seed_products(session, brands, categories, sellers) -> None:
    count = (await session.execute(select(Product))).scalars().first()
    if count is not None:
        logger.info("Products already present — skipping product seed.")
        return

    seller_list = list(sellers.values())
    for idx, (
        cat_slug,
        brand_slug,
        name_ru,
        name_uz,
        article,
        oem,
        part_brand,
        price,
        stock,
        warranty,
        engine,
    ) in enumerate(data.DEMO_PRODUCTS):
        category = categories.get(cat_slug)
        brand = brands.get(brand_slug)
        if category is None:
            continue
        seller = seller_list[idx % len(seller_list)]
        product = Product(
            seller_id=seller.id,
            category_id=category.id,
            name_ru=name_ru,
            name_uz=name_uz,
            article=article,
            oem_number=oem,
            part_brand=part_brand,
            engine=engine,
            description_ru=f"{name_ru} для грузовых автомобилей.",
            description_uz=f"{name_uz} yuk mashinalari uchun.",
            price=Decimal(str(price)),
            stock_qty=stock,
            warranty=warranty,
            status=ProductStatus.approved,
            is_active=True,
        )
        session.add(product)
        await session.flush()
        if brand is not None:
            session.add(ProductVehicle(product_id=product.id, truck_brand_id=brand.id))
    await session.flush()
    logger.info("Seeded %d demo products.", len(data.DEMO_PRODUCTS))


async def seed_analogs(session) -> None:
    existing = (await session.execute(select(AnalogGroup))).scalars().first()
    if existing is not None:
        logger.info("Analog groups already present — skipping.")
        return
    for title, numbers in data.ANALOG_GROUPS:
        group = AnalogGroup(title=title)
        session.add(group)
        await session.flush()
        for number, brand, is_original in numbers:
            session.add(
                AnalogReference(
                    group_id=group.id,
                    number=normalize_part_number(number),
                    number_raw=number,
                    brand=brand,
                    is_original=is_original,
                )
            )
    await session.flush()
    logger.info("Seeded %d analog groups.", len(data.ANALOG_GROUPS))


async def attach_images(session) -> None:
    """Copy generated illustrations into media and attach to demo products lacking images."""
    dest_dir = MEDIA_ROOT / "products"
    dest_dir.mkdir(parents=True, exist_ok=True)
    result = await session.execute(select(Product).options(selectinload(Product.images)))
    attached = 0
    for product in result.scalars().all():
        if product.images:
            continue
        fname = PRODUCT_IMAGE_BY_ARTICLE.get(product.article)
        if not fname:
            continue
        src = _IMAGES_SRC / fname
        if not src.exists():
            continue
        if not (dest_dir / fname).exists():
            shutil.copyfile(src, dest_dir / fname)
        session.add(ProductImage(product_id=product.id, path=f"products/{fname}", sort_order=0))
        attached += 1
    await session.flush()
    if attached:
        logger.info("Attached %d product images.", attached)


async def set_demo_bonuses(session) -> None:
    """Give demo products a master-bonus (~3% of price) if not set yet."""
    from decimal import ROUND_HALF_UP

    result = await session.execute(select(Product).where(Product.bonus == 0))
    updated = 0
    for p in result.scalars().all():
        p.bonus = (Decimal(p.price) * Decimal("0.03")).quantize(
            Decimal("100"), rounding=ROUND_HALF_UP
        )
        updated += 1
    await session.flush()
    if updated:
        logger.info("Set bonus on %d products.", updated)


async def main() -> None:
    async with SessionLocal() as session:
        brands = await seed_brands(session)
        categories = await seed_categories(session)
        await seed_settings(session)
        sellers = await seed_users(session)
        await seed_products(session, brands, categories, sellers)
        await seed_analogs(session)
        await attach_images(session)
        await set_demo_bonuses(session)
        await session.commit()
    logger.info("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
