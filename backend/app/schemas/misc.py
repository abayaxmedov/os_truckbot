from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import MessageKind


# ---- Reviews ----
class ReviewCreate(BaseModel):
    seller_order_id: int
    stars: int = Field(ge=1, le=5)
    comment: str = ""


class ReviewOut(BaseModel):
    id: int
    seller_order_id: int
    seller_id: int
    stars: int
    comment: str = ""
    created_at: str


# ---- Messages (product Q&A / order chat) ----
class MessageCreate(BaseModel):
    to_user_id: int | None = None  # resolved from product/order if omitted
    product_id: int | None = None
    order_id: int | None = None
    kind: MessageKind = MessageKind.general
    text: str


class MessageOut(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    kind: str
    product_id: int | None = None
    order_id: int | None = None
    text: str
    is_read: bool = False
    created_at: str


# ---- Favorites ----
class FavoriteProductIn(BaseModel):
    product_id: int


class FavoriteSellerIn(BaseModel):
    seller_id: int
