from __future__ import annotations

from pydantic import BaseModel

from app.models.enums import DeliveryMethod, PaymentProvider


class OrderCreate(BaseModel):
    contact_name: str
    phone: str
    city: str = ""
    address: str = ""
    comment: str = ""
    delivery_method: DeliveryMethod = DeliveryMethod.delivery
    payment_method: PaymentProvider = PaymentProvider.cash


class OrderItemOut(BaseModel):
    id: int
    product_id: int | None = None
    product_name: str
    article: str = ""
    unit_price: float
    quantity: int
    line_total: float
    image: str | None = None


class SellerOrderOut(BaseModel):
    id: int
    seller_id: int
    seller_name: str = ""
    status: str
    subtotal: float
    commission_amount: float
    seller_payout: float
    items: list[OrderItemOut] = []
    can_review: bool = False
    reviewed: bool = False


class OrderOut(BaseModel):
    id: int
    status_summary: str  # overall status derived from seller orders
    contact_name: str
    phone: str
    city: str = ""
    address: str = ""
    comment: str = ""
    delivery_method: str
    payment_method: str
    payment_status: str
    subtotal: float
    discount: float
    delivery_cost: float
    total: float
    created_at: str
    seller_orders: list[SellerOrderOut] = []


class OrderListItem(BaseModel):
    id: int
    status_summary: str
    total: float
    payment_status: str
    items_count: int
    created_at: str


class SellerOrderRow(BaseModel):
    """A seller's view of their portion of an order (includes buyer/delivery info)."""

    id: int
    order_id: int
    status: str
    buyer_name: str
    phone: str
    city: str = ""
    address: str = ""
    comment: str = ""
    delivery_method: str = "delivery"
    subtotal: float
    commission_amount: float
    seller_payout: float
    items: list[OrderItemOut] = []
    created_at: str


class OrderStatusUpdate(BaseModel):
    status: str


class PayRequest(BaseModel):
    provider: PaymentProvider = PaymentProvider.cash


class PayResponse(BaseModel):
    payment_url: str = ""
    provider: str
    status: str
