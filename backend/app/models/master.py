from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import BonusStatus, MasterStatus, PayoutStatus

if TYPE_CHECKING:
    from app.models.order import Order, SellerOrder
    from app.models.user import User


class MasterProfile(Base, TimestampMixin):
    """A "usta" (master / mechanic): earns per-product bonuses on their orders,
    paid out to a bank card on a recurring cycle."""

    __tablename__ = "master_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    photo: Mapped[str] = mapped_column(String(512), default="")
    address: Mapped[str] = mapped_column(String(512), default="")
    card_number: Mapped[str] = mapped_column(String(32), default="")  # payout bank card
    status: Mapped[MasterStatus] = mapped_column(
        Enum(MasterStatus, native_enum=False, length=16), default=MasterStatus.active
    )

    # --- Service profile (B1) ---
    trucks: Mapped[str] = mapped_column(String(255), default="")  # CSV of truck brand slugs
    specializations: Mapped[str] = mapped_column(String(512), default="")  # CSV of spec codes
    regions: Mapped[str] = mapped_column(String(255), default="")  # areas served (free text)
    work_hours: Mapped[str] = mapped_column(String(64), default="")  # e.g. "9:00–20:00"
    is_24_7: Mapped[bool] = mapped_column(Boolean, default=False)
    experience_years: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bio: Mapped[str] = mapped_column(Text, default="")
    price_call: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)  # call-out
    price_diagnostics: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    price_repair_note: Mapped[str] = mapped_column(String(64), default="")  # e.g. "kelishiladi"
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)  # admin-granted badge

    balance: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))  # withdrawable
    pending: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0")
    )  # not yet completed
    total_earned: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    next_payout_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="master_profile")
    transactions: Mapped[list[BonusTransaction]] = relationship(
        back_populates="master", cascade="all, delete-orphan"
    )
    payouts: Mapped[list[Payout]] = relationship(
        back_populates="master", cascade="all, delete-orphan"
    )


class BonusTransaction(Base, TimestampMixin):
    """Ledger of bonus credits earned by a master (one per seller-order)."""

    __tablename__ = "bonus_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    master_id: Mapped[int] = mapped_column(
        ForeignKey("master_profiles.id", ondelete="CASCADE"), index=True
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    seller_order_id: Mapped[int | None] = mapped_column(
        ForeignKey("seller_orders.id", ondelete="SET NULL"), nullable=True, index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    status: Mapped[BonusStatus] = mapped_column(
        Enum(BonusStatus, native_enum=False, length=16), default=BonusStatus.pending
    )
    note: Mapped[str] = mapped_column(String(255), default="")

    master: Mapped[MasterProfile] = relationship(back_populates="transactions")
    order: Mapped[Order | None] = relationship()
    seller_order: Mapped[SellerOrder | None] = relationship()


class Payout(Base, TimestampMixin):
    """A scheduled payout of the master's balance to their bank card (admin-approved)."""

    __tablename__ = "payouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    master_id: Mapped[int] = mapped_column(
        ForeignKey("master_profiles.id", ondelete="CASCADE"), index=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    card_number: Mapped[str] = mapped_column(String(32), default="")  # snapshot at payout time
    status: Mapped[PayoutStatus] = mapped_column(
        Enum(PayoutStatus, native_enum=False, length=16), default=PayoutStatus.pending
    )
    note: Mapped[str] = mapped_column(String(255), default="")

    master: Mapped[MasterProfile] = relationship(back_populates="payouts")
