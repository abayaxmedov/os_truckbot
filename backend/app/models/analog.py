from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    pass


class AnalogGroup(Base, TimestampMixin):
    """A group of cross-referenced part numbers (an original + its analogs)."""

    __tablename__ = "analog_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), default="")

    references: Mapped[list[AnalogReference]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )


class AnalogReference(Base):
    """One part number belonging to an analog group.

    Search analogs by original number:
      number -> group -> sibling numbers -> products whose article/oem matches.
    """

    __tablename__ = "analog_references"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("analog_groups.id", ondelete="CASCADE"), index=True
    )
    number: Mapped[str] = mapped_column(String(64), index=True)  # normalized part number
    number_raw: Mapped[str] = mapped_column(String(64), default="")  # as entered
    brand: Mapped[str] = mapped_column(String(64), default="")  # Bosch, FEBI, MAN...
    is_original: Mapped[bool] = mapped_column(Boolean, default=False)

    group: Mapped[AnalogGroup] = relationship(back_populates="references")
