from __future__ import annotations

from pydantic import BaseModel


class TruckModelOut(BaseModel):
    id: int
    name: str


class TruckBrandOut(BaseModel):
    id: int
    name: str
    slug: str
    logo: str = ""
    models: list[TruckModelOut] = []


class CategoryOut(BaseModel):
    id: int
    name: str  # localized
    name_ru: str
    name_uz: str
    slug: str
    parent_id: int | None = None
    commission_override: float | None = None
    sort_order: int = 0
    is_active: bool = True
    children: list[CategoryOut] = []


CategoryOut.model_rebuild()
