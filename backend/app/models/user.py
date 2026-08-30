from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import Language, SellerStatus

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.master import MasterProfile
    from app.models.order import Order, SellerOrder
    from app.models.product import Product
    from app.models.review import Review


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(64), default="")
    first_name: Mapped[str] = mapped_column(String(128), default="")
    last_name: Mapped[str] = mapped_column(String(128), default="")
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    language: Mapped[Language] = mapped_column(
        Enum(Language, native_enum=False, length=8), default=Language.ru
    )
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    onboarded: Mapped[bool] = mapped_column(Boolean, default=False)

    seller_profile: Mapped[SellerProfile | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    master_profile: Mapped[MasterProfile | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    cart: Mapped[Cart | None] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    orders: Mapped[list[Order]] = relationship(back_populates="buyer")

    @property
    def full_name(self) -> str:
        return " ".join(p for p in (self.first_name, self.last_name) if p).strip()

    @property
    def is_seller(self) -> bool:
        return self.seller_profile is not None

    @property
    def is_master(self) -> bool:
        return self.master_profile is not None


class SellerProfile(Base, TimestampMixin):
    __tablename__ = "seller_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    shop_name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(1024), default="")
    status: Mapped[SellerStatus] = mapped_column(
        Enum(SellerStatus, native_enum=False, length=16), default=SellerStatus.active
    )
    # NULL -> fall back to category/global commission
    commission_override: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)

    # Cached rating aggregates
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("0"))
    orders_count: Mapped[int] = mapped_column(Integer, default=0)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)
    completion_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))

    user: Mapped[User] = relationship(back_populates="seller_profile")
    products: Mapped[list[Product]] = relationship(back_populates="seller")
    seller_orders: Mapped[list[SellerOrder]] = relationship(back_populates="seller")
    reviews: Mapped[list[Review]] = relationship(back_populates="seller")
