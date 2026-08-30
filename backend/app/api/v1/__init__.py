from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    admin,
    auth,
    cart,
    catalog,
    favorites,
    interactions,
    master,
    me,
    orders,
    payments,
    products,
    public,
    seller,
    uploads,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(me.router)
api_router.include_router(catalog.router)
api_router.include_router(public.router)
api_router.include_router(products.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
api_router.include_router(favorites.router)
api_router.include_router(interactions.router)
api_router.include_router(master.router)
api_router.include_router(seller.router)
api_router.include_router(admin.router)
api_router.include_router(payments.router)
api_router.include_router(uploads.router)
