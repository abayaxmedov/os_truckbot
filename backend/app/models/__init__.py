"""Import all models so their tables register on Base.metadata."""

from app.models.analog import AnalogGroup, AnalogReference
from app.models.banner import Banner
from app.models.cart import Cart, CartItem
from app.models.catalog import Category, TruckBrand, TruckModel
from app.models.enums import (
    DeliveryMethod,
    Language,
    MessageKind,
    OrderStatus,
    PaymentProvider,
    PaymentStatus,
    ProductStatus,
    SellerStatus,
)
from app.models.favorite import FavoriteProduct, FavoriteSeller
from app.models.master import BonusTransaction, MasterProfile, Payout
from app.models.message import Message
from app.models.order import Order, OrderItem, SellerOrder
from app.models.payment import Payment
from app.models.product import Product, ProductImage, ProductVehicle
from app.models.review import Review
from app.models.setting import Setting
from app.models.user import SellerProfile, User

__all__ = [
    "AnalogGroup",
    "AnalogReference",
    "Banner",
    "Cart",
    "CartItem",
    "Category",
    "TruckBrand",
    "TruckModel",
    "DeliveryMethod",
    "Language",
    "MessageKind",
    "OrderStatus",
    "PaymentProvider",
    "PaymentStatus",
    "ProductStatus",
    "SellerStatus",
    "FavoriteProduct",
    "FavoriteSeller",
    "BonusTransaction",
    "MasterProfile",
    "Payout",
    "Message",
    "Order",
    "OrderItem",
    "SellerOrder",
    "Payment",
    "Product",
    "ProductImage",
    "ProductVehicle",
    "Review",
    "Setting",
    "SellerProfile",
    "User",
]
