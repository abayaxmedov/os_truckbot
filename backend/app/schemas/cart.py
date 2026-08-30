from __future__ import annotations

from pydantic import BaseModel, Field


class CartItemIn(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemOut(BaseModel):
    id: int
    product_id: int
    name: str
    article: str = ""
    price: float
    quantity: int
    line_total: float
    image: str | None = None
    stock_qty: int = 0
    seller_id: int
    seller_name: str = ""


class CartOut(BaseModel):
    id: int
    items: list[CartItemOut] = []
    subtotal: float = 0.0
    count: int = 0
