from __future__ import annotations

import asyncio
import contextlib
import logging

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.bonus import run_scheduled_payouts

logger = logging.getLogger(__name__)

_task: asyncio.Task | None = None


async def _loop() -> None:
    while True:
        try:
            async with SessionLocal() as session:
                created = await run_scheduled_payouts(session)
                await session.commit()
                if created:
                    logger.info("Payout cycle: generated %d payout(s).", created)
        except Exception:  # noqa: BLE001 - keep the loop alive
            logger.exception("payout scheduler error")
        await asyncio.sleep(settings.payout_check_interval_seconds)


def start_scheduler() -> None:
    """Start the recurring master-bonus payout cycle (every payout_check_interval_seconds)."""
    global _task
    if _task is None:
        _task = asyncio.create_task(_loop())
        logger.info("Payout scheduler started (period=%d days).", settings.payout_period_days)


async def stop_scheduler() -> None:
    global _task
    if _task is not None:
        _task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await _task
        _task = None
