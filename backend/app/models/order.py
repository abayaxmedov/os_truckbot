from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import DeliveryMethod, OrderStatus, PaymentProvider, PaymentStatus

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.review import Review
    from app.models.user import SellerProfile, User


class Order(Base, TimestampMixin):
    """Parent checkout. Splits into one SellerOrder per seller."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)

    # Delivery / contact info
    contact_name: Mapped[str] = mapped_column(String(128))
    phone: Mapped[str] = mapped_column(String(32))
    city: Mapped[str] = mapped_column(String(128), default="")
    address: Mapped[str] = mapped_column(String(512), default="")
    # Delivery location (sent from Telegram/geolocation at checkout)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    delivery_method: Mapped[DeliveryMethod] = mapped_column(
        Enum(DeliveryMethod, native_enum=False, length=16), default=DeliveryMethod.delivery
    )
    comment: Mapped[str] = mapped_column(Text, default="")

    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    discount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    delivery_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))

    payment_method: Mapped[PaymentProvider] = mapped_column(
        Enum(PaymentProvider, native_enum=False, length=16), default=PaymentProvider.cash
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False, length=16), default=PaymentStatus.pending
    )

    buyer: Mapped[User] = relationship(back_populates="orders")
    seller_orders: Mapped[list[SellerOrder]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class SellerOrder(Base, TimestampMixin):
    """The portion of an Order belonging to a single seller (own status + commission)."""

    __tablename__ = "seller_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("seller_profiles.id", ondelete="RESTRICT"), index=True
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False, length=16), default=OrderStatus.new
    )
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    commission_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    seller_payout: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    # Master-bonus total for this sub-order; settled to the master's balance on completion.
    bonus_total: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    bonus_settled: Mapped[bool] = mapped_column(Boolean, default=False)

    order: Mapped[Order] = relationship(back_populates="seller_orders")
    seller: Mapped[SellerProfile] = relationship(back_populates="seller_orders")
    items: Mapped[list[OrderItem]] = relationship(
        back_populates="seller_order", cascade="all, delete-orphan"
    )
    review: Mapped[Review | None] = relationship(back_populates="seller_order", uselist=False)


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    seller_order_id: Mapped[int] = mapped_column(
        ForeignKey("seller_orders.id", ondelete="CASCADE"), index=True
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Snapshots (immutable historical record, independent of later product edits)
    product_name: Mapped[str] = mapped_column(String(255))
    article: Mapped[str] = mapped_column(String(64), default="")
    unit_price: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    line_total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    commission_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0"))
    bonus: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0")
    )  # per-unit snapshot

    seller_order: Mapped[SellerOrder] = relationship(back_populates="items")
    product: Mapped[Product | None] = relationship()
