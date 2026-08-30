from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.order import SellerOrder
    from app.models.user import SellerProfile, User


class Review(Base, TimestampMixin):
    """1–5 star rating a buyer leaves for a seller after a completed order."""

    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    seller_order_id: Mapped[int] = mapped_column(
        ForeignKey("seller_orders.id", ondelete="CASCADE"), unique=True, index=True
    )
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("seller_profiles.id", ondelete="CASCADE"), index=True
    )
    stars: Mapped[int] = mapped_column(Integer)  # 1..5
    comment: Mapped[str] = mapped_column(String(1024), default="")

    seller_order: Mapped[SellerOrder] = relationship(back_populates="review")
    buyer: Mapped[User] = relationship()
    seller: Mapped[SellerProfile] = relationship(back_populates="reviews")
