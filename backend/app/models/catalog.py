from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class TruckBrand(Base, TimestampMixin):
    """Vehicle make: MAN, Volvo, DAF, Scania, Mercedes-Benz, Renault Trucks, Iveco."""

    __tablename__ = "truck_brands"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    logo: Mapped[str] = mapped_column(String(255), default="")
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    models: Mapped[list[TruckModel]] = relationship(
        back_populates="brand", cascade="all, delete-orphan"
    )


class TruckModel(Base, TimestampMixin):
    __tablename__ = "truck_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand_id: Mapped[int] = mapped_column(
        ForeignKey("truck_brands.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(128))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    brand: Mapped[TruckBrand] = relationship(back_populates="models")


class Category(Base, TimestampMixin):
    """Bilingual, hierarchical product category. Admin CRUD."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name_ru: Mapped[str] = mapped_column(String(128))
    name_uz: Mapped[str] = mapped_column(String(128))
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # NULL -> fall back to global commission
    commission_override: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    parent: Mapped[Category | None] = relationship(remote_side="Category.id", backref="children")
    products: Mapped[list[Product]] = relationship(back_populates="category")

    def name(self, lang: str = "ru") -> str:
        return self.name_uz if lang == "uz" else self.name_ru
