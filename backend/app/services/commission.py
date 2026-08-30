from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.catalog import Category
from app.models.product import Product
from app.models.user import SellerProfile
from app.services.settings_service import get_default_commission

_CENT = Decimal("0.01")


def effective_commission(
    seller_override: Decimal | None,
    category_override: Decimal | None,
    default_percent: Decimal,
) -> Decimal:
    """Resolve commission %: seller override → category override → global default."""
    if seller_override is not None:
        return Decimal(seller_override)
    if category_override is not None:
        return Decimal(category_override)
    return Decimal(default_percent)


def split_amount(amount: Decimal, percent: Decimal) -> tuple[Decimal, Decimal]:
    """Return (marketplace_commission, seller_payout) for an amount and percent.

    Example (TZ §12): 1_000_000 @ 7% -> (70_000, 930_000).
    """
    amount = Decimal(amount)
    commission = (amount * Decimal(percent) / Decimal(100)).quantize(_CENT, rounding=ROUND_HALF_UP)
    payout = (amount - commission).quantize(_CENT, rounding=ROUND_HALF_UP)
    return commission, payout


async def resolve_product_commission(
    session: AsyncSession,
    product: Product,
    seller: SellerProfile,
    category: Category | None,
) -> Decimal:
    default = await get_default_commission(session)
    return effective_commission(
        seller.commission_override,
        category.commission_override if category else None,
        default,
    )
