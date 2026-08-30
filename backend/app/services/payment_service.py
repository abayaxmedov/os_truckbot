from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import PaymentProvider as ProviderEnum
from app.models.enums import PaymentStatus
from app.models.order import Order
from app.models.payment import Payment
from app.services.payments import get_provider


class PaymentError(ValueError):
    pass


async def start_payment(session: AsyncSession, order: Order, provider: ProviderEnum) -> Payment:
    if provider == ProviderEnum.cash:
        order.payment_method = ProviderEnum.cash
        order.payment_status = PaymentStatus.pending
        payment = Payment(
            order_id=order.id,
            provider=ProviderEnum.cash,
            amount=order.total,
            status=PaymentStatus.pending,
        )
        session.add(payment)
        await session.flush()
        return payment

    impl = get_provider(provider)
    init = await impl.create_payment(order.id, order.total)
    order.payment_method = provider
    order.payment_status = PaymentStatus.pending
    payment = Payment(
        order_id=order.id,
        provider=provider,
        amount=order.total,
        status=init.status,
        provider_txn_id=init.provider_txn_id,
        payment_url=init.payment_url,
    )
    session.add(payment)
    await session.flush()
    return payment


async def process_callback(
    session: AsyncSession, provider: ProviderEnum, payload: dict
) -> Payment | None:
    impl = get_provider(provider)
    result = await impl.handle_callback(payload)

    order = await session.get(Order, result.order_id)
    if order is None:
        raise PaymentError("order_not_found")

    payment = (
        (
            await session.execute(
                select(Payment)
                .where(Payment.order_id == order.id, Payment.provider == provider)
                .order_by(Payment.id.desc())
            )
        )
        .scalars()
        .first()
    )
    if payment is None:
        payment = Payment(order_id=order.id, provider=provider, amount=order.total)
        session.add(payment)

    payment.status = result.status
    payment.provider_txn_id = result.provider_txn_id or payment.provider_txn_id
    payment.raw_payload = json.dumps(payload, ensure_ascii=False)
    order.payment_status = result.status
    await session.flush()
    return payment
