from __future__ import annotations

import uuid
from decimal import Decimal

from app.core.config import settings
from app.models.enums import PaymentProvider as ProviderEnum
from app.models.enums import PaymentStatus
from app.services.payments.base import CallbackResult, PaymentInit, PaymentProviderBase


class _StubProvider(PaymentProviderBase):
    provider: ProviderEnum

    async def create_payment(self, order_id: int, amount: Decimal) -> PaymentInit:
        txn = f"stub-{self.provider.value}-{uuid.uuid4().hex[:12]}"
        base = settings.public_base_url.rstrip("/")
        # A real provider would return its hosted checkout URL. The stub points at a
        # local mock-callback endpoint so the flow can be exercised end-to-end.
        url = f"{base}/api/v1/payments/{self.provider.value}/mock?order_id={order_id}&txn={txn}"
        return PaymentInit(payment_url=url, provider_txn_id=txn, status=PaymentStatus.pending)

    async def handle_callback(self, payload: dict) -> CallbackResult:
        # Stub: trust the payload. Real providers verify a signature here.
        order_id = int(payload.get("order_id", 0))
        status_raw = str(payload.get("status", "paid")).lower()
        status = (
            PaymentStatus.paid if status_raw in ("paid", "success", "1") else PaymentStatus.failed
        )
        return CallbackResult(
            order_id=order_id, status=status, provider_txn_id=str(payload.get("txn", ""))
        )


class ClickProvider(_StubProvider):
    provider = ProviderEnum.click


class PaymeProvider(_StubProvider):
    provider = ProviderEnum.payme


class UzumProvider(_StubProvider):
    provider = ProviderEnum.uzum
