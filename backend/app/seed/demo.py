"""Rich demo data for showing the app to a client.

Idempotent: re-running does nothing once the demo marker user exists.
Demo users use NEGATIVE telegram ids so they can never collide with a real
Telegram account (real ids are always positive); they are display-only.

Run:  python -m app.seed.demo        (inside the backend container / venv)
"""
from __future__ import annotations

import asyncio
import logging
import random
import shutil
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.banner import Banner
from app.models.catalog import Category, TruckBrand
from app.models.enums import (
    MasterStatus,
    MessageKind,
    OrderStatus,
    PayoutStatus,
    ProductStatus,
    SellerStatus,
)
from app.models.favorite import FavoriteProduct, FavoriteSeller
from app.models.master import MasterProfile, Payout
from app.models.message import Message
from app.models.product import Product, ProductImage, ProductVehicle
from app.models.user import SellerProfile, User
from app.services.orders import CheckoutInput, create_order, get_or_create_cart, update_seller_order_status
from app.services.ratings import add_review
from app.services.media import MEDIA_ROOT

logger = logging.getLogger("seed.demo")

MARKER_TG = -910000001  # first demo seller; presence means demo data already seeded

_IMAGES_SRC = Path(__file__).resolve().parent / "images"
_IMAGE_FILES = [p.name for p in _IMAGES_SRC.glob("*.svg")]

COUNTRIES = ["de", "tr", "cn", "kr", "us", "it", "se", "pl", "jp"]

SELLERS = [
    ("TruckParts Toshkent", "Оригинальные и аналоговые запчасти для еврофур."),
    ("Avto MAN Servis", "Запчасти MAN, оптом и в розницу."),
    ("Volvo Zapchast", "Всё для Volvo и Renault Trucks."),
    ("DAF Center", "Кабина, ходовая, тормоза DAF."),
    ("Scania Parts UZ", "Двигатель и КПП Scania."),
    ("Mercedes Truck Store", "Actros / Axor запчасти."),
    ("Euro Diesel", "Топливная аппаратура, форсунки, ТНВД."),
    ("Pnevmo Sistema", "Пневматика, ресиверы, краны, EBS/ABS."),
    ("Filtr Market", "Фильтры всех марок, масла, жидкости."),
    ("Podshipnik Savdo", "Подшипники, сальники, ремни, ролики."),
]

MASTERS = [
    ("Akmal", "Yusupov", ["man", "daf", "mercedes-benz"], ["elektrik", "diagnostika", "ebs_abs", "dvigatel"], 8, True),
    ("Sardor", "Karimov", ["volvo", "scania", "iveco"], ["tormoz", "pnevmo", "xodovaya"], 5, True),
    ("Bekzod", "Toshmatov", ["man", "daf", "renault-trucks"], ["dvigatel", "forsunka", "turbina", "adblue"], 12, True),
    ("Jasur", "Aliyev", ["mercedes-benz", "man"], ["elektrik", "ecu", "diagnostika", "ebs_abs"], 7, False),
    ("Otabek", "Rahimov", ["scania", "volvo"], ["kpp", "dvigatel", "sovutish"], 10, True),
    ("Sanjar", "Ismoilov", ["daf", "iveco"], ["shina", "tormoz", "pnevmo"], 4, False),
    ("Dilshod", "Nazarov", ["man", "volvo", "daf"], ["payvandlash", "xodovaya", "tormoz"], 15, True),
    ("Farrux", "Qodirov", ["mercedes-benz", "scania"], ["forsunka", "turbina", "adblue", "ecu"], 9, True),
    ("Aziz", "Umarov", ["iveco", "renault-trucks"], ["elektrik", "diagnostika"], 3, False),
    ("Shohruh", "Hakimov", ["man", "scania", "volvo", "daf"], ["dvigatel", "kpp", "sovutish", "diagnostika"], 11, True),
]

# (name_ru, name_uz, category_slug, part_brand, base_price)
PARTS = [
    ("Тормозной суппорт", "Tormoz supporti", "tormoznaya-sistema", "Knorr-Bremse", 2800000),
    ("Тормозной барабан", "Tormoz barabani", "tormoznaya-sistema", "BPW", 1450000),
    ("Комплект тормозных колодок", "Tormoz kolodkalari to‘plami", "tormoznaya-sistema", "Textar", 920000),
    ("Форсунка топливная", "Yoqilg‘i forsunkasi", "toplivnaya-sistema", "Bosch", 3600000),
    ("ТНВД", "TNVD nasosi", "toplivnaya-sistema", "Bosch", 8900000),
    ("Топливный насос", "Yoqilg‘i nasosi", "toplivnaya-sistema", "Delphi", 2100000),
    ("Воздушный фильтр", "Havo filtri", "filtry", "MANN", 320000),
    ("Масляный фильтр", "Moy filtri", "filtry", "Fleetguard", 180000),
    ("Салонный фильтр", "Salon filtri", "filtry", "Knecht", 150000),
    ("Комплект сцепления", "Debriyaj to‘plami", "sceplenie", "Sachs", 5400000),
    ("Корзина сцепления", "Debriyaj savati", "sceplenie", "Valeo", 3200000),
    ("Турбокомпрессор", "Turbokompressor", "dvigatel", "Holset", 9800000),
    ("Прокладка ГБЦ", "GBS zichlagichi", "dvigatel", "Elring", 1250000),
    ("Водяной насос", "Suv nasosi", "ohlazhdenie", "Graf", 780000),
    ("Радиатор охлаждения", "Sovutish radiatori", "ohlazhdenie", "Nissens", 4200000),
    ("Интеркулер", "Interkuler", "ohlazhdenie", "Nissens", 3800000),
    ("Амортизатор кабины", "Kabina amortizatori", "amortizatory", "Sachs", 640000),
    ("Амортизатор подвески", "Osma amortizatori", "amortizatory", "Monroe", 720000),
    ("Пневморессора", "Pnevmaressora", "pnevmatika", "Contitech", 1750000),
    ("Кран уровня пола", "Pol sathi krani", "pnevmatika", "Wabco", 1900000),
    ("Осушитель воздуха", "Havo quritgichi", "pnevmatika", "Knorr-Bremse", 2450000),
    ("Стартер", "Starter", "elektrika", "Bosch", 4500000),
    ("Генератор", "Generator", "elektrika", "Bosch", 5200000),
    ("Датчик ABS", "ABS datchigi", "datchiki", "Wabco", 380000),
    ("Датчик коленвала", "Tirsak vali datchigi", "datchiki", "Bosch", 420000),
    ("Ремень приводной", "Uzatma kamari", "remni", "Gates", 175000),
    ("Ролик натяжной", "Taranglash roliki", "remni", "INA", 260000),
    ("Подшипник ступицы", "Stupitsa podshipnigi", "podshipniki", "SKF", 1350000),
    ("Крестовина карданная", "Kardan krestovinasi", "podshipniki", "Spicer", 540000),
    ("Наконечник рулевой", "Rul nakonechnigi", "rulevoe-upravlenie", "Lemförder", 480000),
    ("Тяга рулевая", "Rul tortqisi", "rulevoe-upravlenie", "TRW", 1150000),
    ("Масло моторное 10W-40 20л", "Motor moyi 10W-40 20l", "masla-zhidkosti", "Petronas", 980000),
    ("Антифриз концентрат 5л", "Antifriz konsentrat 5l", "masla-zhidkosti", "Mobil", 320000),
    ("Фара передняя", "Old faralar", "zapchasti-kabiny", "Hella", 2600000),
    ("Зеркало заднего вида", "Orqa ko‘rish oynasi", "zapchasti-kabiny", "Mekra", 890000),
    ("Комплект AdBlue насоса", "AdBlue nasosi to‘plami", "drugie", "Bosch", 4100000),
]

TRUCK_SLUGS = ["man", "volvo", "daf", "scania", "mercedes-benz", "renault-trucks", "iveco"]
UZ_CITIES = ["г. Ташкент", "Ташкентская обл.", "г. Самарканд", "г. Бухара", "г. Наманган", "г. Андижан", "г. Фергана"]
QUESTIONS = [
    "Здравствуйте, есть в наличии?", "Оригинал или аналог?", "Какая гарантия на эту деталь?",
    "Подойдёт на MAN TGX 2018?", "Можно доставку в Самарканд?", "Какой срок поставки?",
    "Дайте оптовую цену на 5 штук", "Это точно на DAF XF?", "Есть сертификат качества?",
    "Можно фото реального товара?",
]
REVIEW_TEXTS = [
    "Всё пришло быстро, качество отличное!", "Оригинал, подошло идеально.", "Хороший продавец, рекомендую.",
    "Цена немного выше, но качество на уровне.", "Быстрая доставка, спасибо!", "Деталь рабочая, претензий нет.",
    "Помогли с подбором, всё чётко.", "Упаковка хорошая, товар целый.", "Возьму ещё, всё понравилось.",
    "Отличный магазин запчастей.",
]


def _q100(x: Decimal) -> Decimal:
    return x.quantize(Decimal("100"), rounding=ROUND_HALF_UP)


async def _already_seeded(session) -> bool:
    row = await session.execute(select(User).where(User.telegram_id == MARKER_TG))
    return row.scalar_one_or_none() is not None


async def main() -> None:
    async with SessionLocal() as session:
        if await _already_seeded(session):
            logger.info("Demo data already present — skipping.")
            print("Demo data already present — nothing to do.")
            return

        rnd = random.Random(2208)  # deterministic
        cats = {c.slug: c for c in (await session.execute(select(Category))).scalars().all()}
        brands = {b.slug: b for b in (await session.execute(select(TruckBrand))).scalars().all()}

        # ---- Sellers (10) ----
        seller_profiles: list[SellerProfile] = []
        for i, (shop, desc) in enumerate(SELLERS):
            u = User(telegram_id=MARKER_TG - i, username=f"demo_seller_{i+1}",
                     first_name=shop.split()[0], last_name="", phone=f"+9989011100{i:02d}", onboarded=True)
            session.add(u)
            await session.flush()
            sp = SellerProfile(user_id=u.id, shop_name=shop, description=desc, status=SellerStatus.active)
            session.add(sp)
            await session.flush()
            seller_profiles.append(sp)
        logger.info("Seeded %d demo sellers.", len(seller_profiles))

        # ---- Products (~35) ----
        dest_dir = MEDIA_ROOT / "products"
        dest_dir.mkdir(parents=True, exist_ok=True)
        for fn in _IMAGE_FILES:
            if not (dest_dir / fn).exists():
                shutil.copyfile(_IMAGES_SRC / fn, dest_dir / fn)

        products: list[Product] = []
        for idx, (nru, nuz, cat_slug, brand, base) in enumerate(PARTS):
            cat = cats.get(cat_slug) or next(iter(cats.values()))
            sp = seller_profiles[idx % len(seller_profiles)]
            price = _q100(Decimal(base) * Decimal(str(rnd.uniform(0.9, 1.15))))
            p = Product(
                seller_id=sp.id, category_id=cat.id, name_ru=nru, name_uz=nuz,
                article=f"{brand[:3].upper()}{1000+idx}", oem_number=f"{rnd.randint(10,99)}.{rnd.randint(10000,99999)}-{rnd.randint(1000,9999)}",
                part_brand=brand, country=rnd.choice(COUNTRIES), engine="",
                description_ru=f"{nru} для грузовых автомобилей. Оригинальное качество, гарантия.",
                description_uz=f"{nuz} yuk mashinalari uchun. Original sifat, kafolat.",
                price=price, stock_qty=rnd.randint(3, 60), warranty=rnd.choice(["6 мес", "12 мес", "12 мес", ""]),
                bonus=_q100(price * Decimal("0.03")), status=ProductStatus.approved, is_active=True,
                views=rnd.randint(5, 400),
            )
            session.add(p)
            await session.flush()
            fn = _IMAGE_FILES[idx % len(_IMAGE_FILES)]
            session.add(ProductImage(product_id=p.id, path=f"products/{fn}", sort_order=0))
            # 1-2 compatible truck brands
            for slug in rnd.sample(TRUCK_SLUGS, rnd.randint(1, 2)):
                if slug in brands:
                    session.add(ProductVehicle(product_id=p.id, truck_brand_id=brands[slug].id))
            products.append(p)
        await session.flush()
        logger.info("Seeded %d demo products.", len(products))

        # ---- Masters (10) ----
        from datetime import UTC, datetime, timedelta
        base_lat, base_lng = 41.3111, 69.2797
        master_users: list[User] = []
        for i, (fn_, ln, trucks, specs, exp, verified) in enumerate(MASTERS):
            u = User(telegram_id=MARKER_TG - 2000 - i, username=f"demo_master_{i+1}",
                     first_name=fn_, last_name=ln, phone=f"+9989022200{i:02d}", onboarded=True)
            session.add(u)
            await session.flush()
            mp = MasterProfile(
                user_id=u.id, status=MasterStatus.active,
                trucks=",".join(trucks), specializations=",".join(specs),
                regions=rnd.choice(UZ_CITIES), work_hours=rnd.choice(["9:00–20:00", "8:00–19:00", "24/7"]),
                is_24_7=(i % 3 == 0), experience_years=exp,
                bio=f"{fn_} {ln} — yuk mashinalari ustasi, {exp} yil tajriba.",
                price_call=_q100(Decimal(rnd.choice([400000, 500000, 600000, 700000]))),
                price_diagnostics=_q100(Decimal(rnd.choice([120000, 150000, 200000]))),
                price_repair_note="kelishiladi", is_verified=verified,
                latitude=Decimal(str(round(base_lat + rnd.uniform(-0.12, 0.12), 6))),
                longitude=Decimal(str(round(base_lng + rnd.uniform(-0.15, 0.15), 6))),
                next_payout_at=datetime.now(UTC) + timedelta(days=rnd.randint(1, 12)),
            )
            session.add(mp)
            master_users.append(u)
        await session.flush()
        logger.info("Seeded %d demo masters.", len(MASTERS))

        # ---- Buyers (10) ----
        buyers: list[User] = []
        for i in range(10):
            u = User(telegram_id=MARKER_TG - 3000 - i, username=f"demo_buyer_{i+1}",
                     first_name=rnd.choice(["Alisher", "Kamol", "Rustam", "Bobur", "Ulug‘bek", "Doston", "Javohir"]),
                     last_name="", phone=f"+9989033300{i:02d}", onboarded=True)
            session.add(u)
            buyers.append(u)
        await session.flush()
        logger.info("Seeded %d demo buyers.", len(buyers))

        await session.commit()

        # ---- Orders (12) via the real checkout flow (updates sold_count, stats, bonuses) ----
        order_buyers = buyers + master_users[:2]  # a couple of master orders → bonuses
        completed_seller_orders = []
        for i, buyer in enumerate(order_buyers):
            cart = await get_or_create_cart(session, buyer.id)
            from app.models.cart import CartItem
            for p in rnd.sample(products, rnd.randint(1, 3)):
                session.add(CartItem(cart_id=cart.id, product_id=p.id, quantity=rnd.randint(1, 3)))
            await session.flush()
            order = await create_order(session, buyer, CheckoutInput(
                contact_name=buyer.first_name, phone=buyer.phone or "+998900000000",
                city=rnd.choice(UZ_CITIES), address="ул. Демо, 1",
                latitude=round(base_lat + rnd.uniform(-0.1, 0.1), 6),
                longitude=round(base_lng + rnd.uniform(-0.1, 0.1), 6),
            ))
            await session.flush()
            # Advance most orders through a realistic status; complete ~half.
            for so in order.seller_orders:
                status = rnd.choice([
                    OrderStatus.completed, OrderStatus.completed, OrderStatus.delivered,
                    OrderStatus.processing, OrderStatus.new, OrderStatus.confirmed,
                ])
                await update_seller_order_status(session, so, status)
                if status == OrderStatus.completed:
                    completed_seller_orders.append((buyer.id, so))
            await session.commit()
        logger.info("Seeded %d demo orders.", len(order_buyers))

        # ---- Reviews (on completed seller-orders) ----
        reviewed = 0
        for buyer_id, so in completed_seller_orders[:12]:
            try:
                await add_review(session, buyer_id, so, rnd.randint(4, 5), rnd.choice(REVIEW_TEXTS))
                reviewed += 1
            except Exception:  # noqa: BLE001 - already reviewed / not completed
                pass
        await session.commit()
        logger.info("Seeded %d demo reviews.", reviewed)

        # ---- Messages (10 buyer questions) ----
        for i in range(10):
            buyer = rnd.choice(buyers)
            p = rnd.choice(products)
            session.add(Message(
                from_user_id=buyer.id, to_user_id=seller_profiles[0].user_id,
                kind=MessageKind.question, product_id=p.id, text=rnd.choice(QUESTIONS),
            ))
        await session.flush()

        # ---- Banners (4) ----
        for i, (title, target) in enumerate([
            ("Скидки на тормозные системы", "/catalog?category_id="),
            ("Оригинальные фильтры", "/catalog?sort=popular"),
            ("Найдите мастера рядом", "/masters"),
            ("Топливная аппаратура Bosch", "/catalog"),
        ]):
            session.add(Banner(title=title, image=f"products/{_IMAGE_FILES[i % len(_IMAGE_FILES)]}",
                               target=target, is_active=(i == 0), sort_order=i))
        await session.flush()

        # ---- Favorites ----
        for buyer in buyers[:6]:
            for p in rnd.sample(products, 3):
                session.add(FavoriteProduct(user_id=buyer.id, product_id=p.id))
            session.add(FavoriteSeller(user_id=buyer.id, seller_id=rnd.choice(seller_profiles).id))
        await session.flush()

        # ---- Payouts (a few, for masters with balance) ----
        masters = (await session.execute(select(MasterProfile).where(MasterProfile.balance > 0))).scalars().all()
        for i, mp in enumerate(masters[:3]):
            amount = mp.balance
            session.add(Payout(master_id=mp.id, amount=amount, card_number="8600123456789012",
                               status=[PayoutStatus.pending, PayoutStatus.paid, PayoutStatus.pending][i % 3]))
        await session.commit()

        logger.info("Demo data seeding complete.")
        print("Demo data seeded: 10 sellers, 10 masters, 10 buyers,",
              f"{len(products)} products, {len(order_buyers)} orders, {reviewed} reviews, banners, messages, favorites.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
