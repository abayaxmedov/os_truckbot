from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.core.deps import SessionDep
from app.models.enums import PaymentProvider as ProviderEnum
from app.schemas.common import Msg
from app.services.payment_service import PaymentError, process_callback

router = APIRouter(prefix="/payments", tags=["payments"])


def _provider(provider: str) -> ProviderEnum:
    try:
        p = ProviderEnum(provider)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="unknown_provider") from exc
    if p == ProviderEnum.cash:
        raise HTTPException(status_code=400, detail="not_online_provider")
    return p


@router.post("/{provider}/callback", response_model=Msg)
async def payment_callback(provider: str, request: Request, session: SessionDep) -> Msg:
    """Gateway → us. Stub trusts the payload; real providers verify a signature here."""
    p = _provider(provider)
    try:
        payload = await request.json()
    except Exception:  # noqa: BLE001
        payload = dict((await request.form()).items())
    try:
        await process_callback(session, p, payload)
        await session.commit()
    except PaymentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return Msg(detail="ok")


@router.get("/{provider}/mock", response_class=HTMLResponse)
async def payment_mock(provider: str, order_id: int, txn: str, session: SessionDep) -> HTMLResponse:
    """Local stub 'hosted checkout' page: marks the order paid, for end-to-end testing."""
    p = _provider(provider)
    try:
        await process_callback(session, p, {"order_id": order_id, "status": "paid", "txn": txn})
        await session.commit()
    except PaymentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return HTMLResponse(
        f"<html><body style='font-family:sans-serif;text-align:center;padding:40px'>"
        f"<h2>✅ Оплата (демо): заказ №{order_id}</h2>"
        f"<p>Провайдер: {p.value}. Транзакция: {txn}.</p>"
        f"<p>Это тестовая страница-заглушка. Реальная интеграция подключается позже.</p>"
        f"</body></html>"
    )
