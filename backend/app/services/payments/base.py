from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from app.models.enums import PaymentProvider as ProviderEnum
from app.models.enums import PaymentStatus


@dataclass
class PaymentInit:
    payment_url: str
    provider_txn_id: str
    status: PaymentStatus = PaymentStatus.pending


@dataclass
class CallbackResult:
    order_id: int
    status: PaymentStatus
    provider_txn_id: str = ""


class PaymentProviderBase(ABC):
    """Common interface for a payment gateway.

    Stub implementations return a mock payment URL and mark the payment pending,
    so the checkout flow is fully testable before merchant keys are provisioned.
    Wiring a real gateway later means filling in these two methods only.
    """

    provider: ProviderEnum

    @abstractmethod
    async def create_payment(self, order_id: int, amount: Decimal) -> PaymentInit: ...

    @abstractmethod
    async def handle_callback(self, payload: dict) -> CallbackResult: ...
