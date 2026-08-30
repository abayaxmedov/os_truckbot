from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, Numeric, String, Text, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import normalize_part_number
from app.db.base import Base, TimestampMixin
from app.models.enums import ProductStatus

if TYPE_CHECKING:
    from app.models.catalog import Category, TruckBrand, TruckModel
    from app.models.user import SellerProfile


class Product(Base, TimestampMixin):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("seller_profiles.id", ondelete="CASCADE"), index=True
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True
    )

    name_ru: Mapped[str] = mapped_column(String(255))
    name_uz: Mapped[str] = mapped_column(String(255), default="")
    article: Mapped[str] = mapped_column(String(64), index=True, default="")  # артикул
    oem_number: Mapped[str] = mapped_column(
        String(64), index=True, default=""
    )  # оригинальный номер
    # Normalized (alphanumeric, upper) forms of article/oem for reliable search & analog matching.
    article_norm: Mapped[str] = mapped_column(String(64), index=True, default="")
    oem_norm: Mapped[str] = mapped_column(String(64), index=True, default="")
    part_brand: Mapped[str] = mapped_column(String(64), index=True, default="")  # Bosch, FEBI...
    engine: Mapped[str] = mapped_column(String(128), default="")
    description_ru: Mapped[str] = mapped_column(Text, default="")
    description_uz: Mapped[str] = mapped_column(Text, default="")

    price: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    currency: Mapped[str] = mapped_column(String(8), default="UZS")
    stock_qty: Mapped[int] = mapped_column(Integer, default=0)
    warranty: Mapped[str] = mapped_column(String(128), default="")
    # Per-unit bonus credited to a "master" (usta) buyer's balance (admin-set).
    bonus: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))

    status: Mapped[ProductStatus] = mapped_column(
        Enum(ProductStatus, native_enum=False, length=16), default=ProductStatus.approved
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    views: Mapped[int] = mapped_column(Integer, default=0)

    seller: Mapped[SellerProfile] = relationship(back_populates="products")
    category: Mapped[Category] = relationship(back_populates="products")
    images: Mapped[list[ProductImage]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.sort_order",
    )
    vehicles: Mapped[list[ProductVehicle]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )

    def name(self, lang: str = "ru") -> str:
        if lang == "uz" and self.name_uz:
            return self.name_uz
        return self.name_ru


@event.listens_for(Product, "before_insert")
@event.listens_for(Product, "before_update")
def _sync_product_norms(mapper, connection, target: Product) -> None:
    target.article_norm = normalize_part_number(target.article or "")
    target.oem_norm = normalize_part_number(target.oem_number or "")


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    path: Mapped[str] = mapped_column(String(512))  # relative media path or URL
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship(back_populates="images")


class ProductVehicle(Base):
    """Compatible vehicle for a product (truck brand + optional model)."""

    __tablename__ = "product_vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    truck_brand_id: Mapped[int] = mapped_column(
        ForeignKey("truck_brands.id", ondelete="CASCADE"), index=True
    )
    truck_model_id: Mapped[int | None] = mapped_column(
        ForeignKey("truck_models.id", ondelete="SET NULL"), nullable=True, index=True
    )

    product: Mapped[Product] = relationship(back_populates="vehicles")
    brand: Mapped[TruckBrand] = relationship()
    model: Mapped[TruckModel | None] = relationship()
