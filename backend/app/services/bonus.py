from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.enums import BonusStatus, OrderStatus, PayoutStatus
from app.models.master import BonusTransaction, MasterProfile, Payout
from app.models.order import Order, SellerOrder

_Z = Decimal("0")


async def credit_pending_on_checkout(
    session: AsyncSession, order: Order, master: MasterProfile
) -> None:
    """A master placed an order → record each sub-order's bonus as *pending*."""
    for so in order.seller_orders:
        bonus_total = sum((oi.bonus * oi.quantity for oi in so.items), _Z)
        so.bonus_total = bonus_total
        so.bonus_settled = False
        if bonus_total <= _Z:
            continue
        master.pending = (master.pending or _Z) + bonus_total
        session.add(
            BonusTransaction(
                master_id=master.id,
                order_id=order.id,
                seller_order_id=so.id,
                amount=bonus_total,
                status=BonusStatus.pending,
                note=f"Заказ #{order.id}",
            )
        )
    await session.flush()


async def _find_txn(session: AsyncSession, seller_order_id: int) -> BonusTransaction | None:
    return (
        await session.execute(
            select(BonusTransaction).where(
                BonusTransaction.seller_order_id == seller_order_id,
                BonusTransaction.status == BonusStatus.pending,
            )
        )
    ).scalar_one_or_none()


async def settle_seller_order_bonus(
    session: AsyncSession, seller_order: SellerOrder, new_status: OrderStatus
) -> None:
    """Move a sub-order's pending bonus to the master's balance (completed) or void it (cancelled)."""
    if seller_order.bonus_settled or (seller_order.bonus_total or _Z) <= _Z:
        return
    if new_status not in (OrderStatus.completed, OrderStatus.cancelled):
        return

    # Resolve the master from the order's buyer
    order = await session.get(Order, seller_order.order_id)
    if order is None:
        return
    master = (
        await session.execute(select(MasterProfile).where(MasterProfile.user_id == order.buyer_id))
    ).scalar_one_or_none()
    if master is None:
        return

    amount = seller_order.bonus_total
    txn = await _find_txn(session, seller_order.id)
    master.pending = max(_Z, (master.pending or _Z) - amount)

    if new_status == OrderStatus.completed:
        master.balance = (master.balance or _Z) + amount
        master.total_earned = (master.total_earned or _Z) + amount
        if txn:
            txn.status = BonusStatus.completed
    else:  # cancelled
        if txn:
            txn.status = BonusStatus.rejected

    seller_order.bonus_settled = True
    await session.flush()


async def run_scheduled_payouts(session: AsyncSession, now: datetime | None = None) -> int:
    """Generate payouts for masters whose 12-day cycle is due and who have a balance."""
    now = now or datetime.now(UTC)
    period = timedelta(days=settings.payout_period_days)
    result = await session.execute(select(MasterProfile))
    created = 0
    for m in result.scalars().all():
        if m.next_payout_at is None:
            m.next_payout_at = now + period
            continue
        if m.next_payout_at <= now:
            if (m.balance or _Z) > _Z:
                session.add(
                    Payout(
                        master_id=m.id,
                        amount=m.balance,
                        card_number=m.card_number,
                        status=PayoutStatus.pending,
                    )
                )
                m.balance = _Z
                created += 1
            # advance to the next cycle even if balance was zero
            m.next_payout_at = now + period
    await session.flush()
    return created


async def approve_payout(session: AsyncSession, payout: Payout) -> None:
    payout.status = PayoutStatus.paid
    await session.flush()


async def reject_payout(session: AsyncSession, payout: Payout) -> None:
    if payout.status == PayoutStatus.pending:
        master = await session.get(MasterProfile, payout.master_id)
        if master is not None:
            master.balance = (master.balance or _Z) + payout.amount
    payout.status = PayoutStatus.rejected
    await session.flush()
