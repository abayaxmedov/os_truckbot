from __future__ import annotations

from app.models.enums import PaymentProvider as ProviderEnum
from app.services.payments.base import PaymentProviderBase
from app.services.payments.stubs import ClickProvider, PaymeProvider, UzumProvider

_PROVIDERS: dict[ProviderEnum, PaymentProviderBase] = {
    ProviderEnum.click: ClickProvider(),
    ProviderEnum.payme: PaymeProvider(),
    ProviderEnum.uzum: UzumProvider(),
}


def get_provider(provider: ProviderEnum) -> PaymentProviderBase:
    if provider not in _PROVIDERS:
        raise ValueError(f"unsupported_provider:{provider}")
    return _PROVIDERS[provider]


def is_online_provider(provider: ProviderEnum) -> bool:
    return provider in _PROVIDERS


__all__ = ["get_provider", "is_online_provider", "PaymentProviderBase"]
