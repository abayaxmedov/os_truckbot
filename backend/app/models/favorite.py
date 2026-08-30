from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import SellerProfile


class FavoriteProduct(Base, TimestampMixin):
    __tablename__ = "favorite_products"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_fav_product"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )

    product: Mapped[Product] = relationship()


class FavoriteSeller(Base, TimestampMixin):
    __tablename__ = "favorite_sellers"
    __table_args__ = (UniqueConstraint("user_id", "seller_id", name="uq_fav_seller"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    seller_id: Mapped[int] = mapped_column(
        ForeignKey("seller_profiles.id", ondelete="CASCADE"), index=True
    )

    seller: Mapped[SellerProfile] = relationship()
