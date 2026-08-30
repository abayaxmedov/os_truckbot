from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin

# Well-known setting keys
KEY_DEFAULT_COMMISSION = "default_commission_percent"
KEY_DEFAULT_DELIVERY_COST = "default_delivery_cost"


class Setting(Base, TimestampMixin):
    """Simple key/value store for global marketplace settings (e.g. default commission)."""

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")
