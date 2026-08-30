from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.models.enums import PaymentProvider, PaymentStatus

if TYPE_CHECKING:
    from app.models.order import Order


class Payment(Base, TimestampMixin):
    """Payment attempt record. Providers are stubbed until merchant keys are supplied."""

    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    provider: Mapped[PaymentProvider] = mapped_column(
        Enum(PaymentProvider, native_enum=False, length=16)
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, native_enum=False, length=16), default=PaymentStatus.pending
    )
    provider_txn_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payment_url: Mapped[str] = mapped_column(String(1024), default="")
    raw_payload: Mapped[str] = mapped_column(Text, default="")  # callback debug

    order: Mapped[Order] = relationship()
