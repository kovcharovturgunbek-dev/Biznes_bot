from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# =========================================================
# 1. ASOSIY BAZA
# =========================================================

class Base(DeclarativeBase):
    pass


def enum_column(enum_class: type[Enum], name: str):
    return SAEnum(
        enum_class,
        name=name,
        native_enum=False,
        validate_strings=True,
        values_callable=lambda items: [item.value for item in items],
    )


# =========================================================
# 2. ENUmlar
# =========================================================

class UserStatus(str, Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"


class SellerApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ProductStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class OrderStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    PROCESSING = "processing"
    PARTIALLY_COMPLETED = "partially_completed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class SellerOrderStatus(str, Enum):
    NEW = "new"
    ACCEPTED = "accepted"
    PREPARING = "preparing"
    READY = "ready"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class ReservationStatus(str, Enum):
    ACTIVE = "active"
    CONSUMED = "consumed"
    RELEASED = "released"
    EXPIRED = "expired"


class ReturnStatus(str, Enum):
    OPEN = "open"
    SELLER_REVIEW = "seller_review"
    ADMIN_REVIEW = "admin_review"
    DIRECTOR_REVIEW = "director_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"
    CLOSED = "closed"


class PayoutStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ON_HOLD = "on_hold"


class PromoType(str, Enum):
    STANDARD_DISCOUNT = "standard_discount"
    CAMPAIGN = "campaign"
    PROMO_CODE = "promo_code"


class MysteryBoxStatus(str, Enum):
    OPENED = "opened"
    AWARDED = "awarded"
    CANCELLED = "cancelled"


# =========================================================
# 3. FOYDALANUVCHILAR
# =========================================================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )

    full_name: Mapped[str | None] = mapped_column(String(255))
    username: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(30))

    status: Mapped[UserStatus] = mapped_column(
        enum_column(UserStatus, "user_status"),
        default=UserStatus.ACTIVE,
        nullable=False,
    )

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# =========================================================
# 4. SOTUVCHILAR
# =========================================================

class SellerApplication(Base):
    __tablename__ = "seller_applications"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    store_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    contact_phone: Mapped[str] = mapped_column(String(30), nullable=False)

    status: Mapped[SellerApplicationStatus] = mapped_column(
        enum_column(SellerApplicationStatus, "seller_application_status"),
        default=SellerApplicationStatus.PENDING,
        nullable=False,
    )

    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )
    review_note: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(primary_key=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    phone: Mapped[str | None] = mapped_column(String(30))

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# =========================================================
# 5. KATEGORIYALAR
# =========================================================

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT")
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# =========================================================
# 6. MAHSULOTLAR
# =========================================================

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    status: Mapped[ProductStatus] = mapped_column(
        enum_column(ProductStatus, "product_status"),
        default=ProductStatus.DRAFT,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    sku: Mapped[str | None] = mapped_column(String(100), unique=True)
    variant_name: Mapped[str | None] = mapped_column(String(150))
    attributes: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_price: Mapped[int | None] = mapped_column(BigInteger)

    total_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        CheckConstraint("price >= 0", name="ck_variant_price_nonnegative"),
        CheckConstraint(
            "original_price IS NULL OR original_price >= 0",
            name="ck_variant_original_price_nonnegative",
        ),
        CheckConstraint("total_stock >= 0", name="ck_variant_stock_nonnegative"),
        CheckConstraint(
            "reserved_stock >= 0 AND reserved_stock <= total_stock",
            name="ck_variant_reserved_stock",
        ),
    )

    @property
    def sellable_stock(self) -> int:
        return self.total_stock - self.reserved_stock


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


# =========================================================
# 7. SAVAT VA SEVIMLILAR
# =========================================================

class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )

    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=False
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_cart_item_quantity_positive"),
        UniqueConstraint("cart_id", "variant_id", name="uq_cart_variant"),
    )


class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "product_id", name="uq_user_favorite_product"),
    )


# =========================================================
# 8. BUYURTMALAR
# =========================================================

class Order(Base):
    """Xaridor uchun bitta umumiy buyurtma."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_number: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[OrderStatus] = mapped_column(
        enum_column(OrderStatus, "order_status"),
        default=OrderStatus.PENDING_PAYMENT,
        nullable=False,
    )

    subtotal: Mapped[int] = mapped_column(BigInteger, nullable=False)
    delivery_total: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    discount_total: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    total_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_order_subtotal"),
        CheckConstraint("delivery_total >= 0", name="ck_order_delivery"),
        CheckConstraint("discount_total >= 0", name="ck_order_discount"),
        CheckConstraint("total_amount >= 0", name="ck_order_total"),
    )


class SellerOrder(Base):
    """Umumiy buyurtmaning muayyan sotuvchiga tegishli qismi."""

    __tablename__ = "seller_orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    status: Mapped[SellerOrderStatus] = mapped_column(
        enum_column(SellerOrderStatus, "seller_order_status"),
        default=SellerOrderStatus.NEW,
        nullable=False,
    )

    subtotal: Mapped[int] = mapped_column(BigInteger, nullable=False)
    delivery_amount: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("order_id", "store_id", name="uq_order_store"),
        CheckConstraint("subtotal >= 0", name="ck_seller_order_subtotal"),
    )


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    seller_order_id: Mapped[int] = mapped_column(
        ForeignKey("seller_orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )

    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"), nullable=False
    )

    # Buyurtma berilgan vaqtdagi mahsulot ma'lumotlari
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    variant_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    unit_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    line_total: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        CheckConstraint("unit_price >= 0", name="ck_order_item_price"),
        CheckConstraint("quantity > 0", name="ck_order_item_quantity"),
        CheckConstraint("line_total >= 0", name="ck_order_item_total"),
    )


# =========================================================
# 9. TO'LOVLAR VA SOTUVCHIGA TO'LOV
# =========================================================

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), unique=True)

    amount: Mapped[int] = mapped_column(BigInteger, nullable=False)

    status: Mapped[PaymentStatus] = mapped_column(
        enum_column(PaymentStatus, "payment_status"),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    idempotency_key: Mapped[str] = mapped_column(
        String(150), unique=True, nullable=False
    )

    provider_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_payment_amount"),
    )


class SellerPayout(Base):
    __tablename__ = "seller_payouts"

    id: Mapped[int] = mapped_column(primary_key=True)

    seller_order_id: Mapped[int] = mapped_column(
        ForeignKey("seller_orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    store_id: Mapped[int] = mapped_column(
        ForeignKey("stores.id", ondelete="RESTRICT"),
        nullable=False,
    )

    gross_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    commission_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)
    net_amount: Mapped[int] = mapped_column(BigInteger, nullable=False)

    status: Mapped[PayoutStatus] = mapped_column(
        enum_column(PayoutStatus, "payout_status"),
        default=PayoutStatus.PENDING,
        nullable=False,
    )

    provider_transfer_id: Mapped[str | None] = mapped_column(String(255))
    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("gross_amount >= 0", name="ck_payout_gross"),
        CheckConstraint("commission_amount >= 0", name="ck_payout_commission"),
        CheckConstraint("net_amount >= 0", name="ck_payout_net"),
    )


# =========================================================
# 10. OMBOR VA VAQTINCHALIK ZAXIRA
# =========================================================

class StockReservation(Base):
    __tablename__ = "stock_reservations"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_item_id: Mapped[int] = mapped_column(
        ForeignKey("order_items.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[ReservationStatus] = mapped_column(
        enum_column(ReservationStatus, "reservation_status"),
        default=ReservationStatus.ACTIVE,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_reservation_quantity"),
    )


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)

    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    changed_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    quantity_change: Mapped[int] = mapped_column(Integer, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# =========================================================
# 11. QAYTARISH VA NIZOLAR
# =========================================================

class ReturnCase(Base):
    __tablename__ = "return_cases"

    id: Mapped[int] = mapped_column(primary_key=True)

    seller_order_id: Mapped[int] = mapped_column(
        ForeignKey("seller_orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    order_item_id: Mapped[int | None] = mapped_column(
        ForeignKey("order_items.id", ondelete="RESTRICT")
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    reason: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    requested_refund: Mapped[int | None] = mapped_column(BigInteger)

    status: Mapped[ReturnStatus] = mapped_column(
        enum_column(ReturnStatus, "return_status"),
        default=ReturnStatus.OPEN,
        nullable=False,
    )

    assigned_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ReturnEvidence(Base):
    __tablename__ = "return_evidence"

    id: Mapped[int] = mapped_column(primary_key=True)

    return_case_id: Mapped[int] = mapped_column(
        ForeignKey("return_cases.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    uploaded_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )

    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# =========================================================
# 12. AKSIYALAR VA PROMO-KODLAR
# =========================================================

class Promotion(Base):
    __tablename__ = "promotions"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    promo_type: Mapped[PromoType] = mapped_column(
        enum_column(PromoType, "promo_type"), nullable=False
    )

    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT")
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT")
    )

    variant_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT")
    )

    discount_percent: Mapped[float | None] = mapped_column(Numeric(5, 2))
    discount_amount: Mapped[int | None] = mapped_column(BigInteger)

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id: Mapped[int] = mapped_column(primary_key=True)

    promotion_id: Mapped[int] = mapped_column(
        ForeignKey("promotions.id", ondelete="RESTRICT"),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    usage_limit: Mapped[int | None] = mapped_column(Integer)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


# =========================================================
# 13. MYSTERY BOX
# =========================================================

class MysteryBoxPrize(Base):
    __tablename__ = "mystery_box_prizes"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    prize_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    prize_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class MysteryBoxAttempt(Base):
    __tablename__ = "mystery_box_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    prize_id: Mapped[int | None] = mapped_column(
        ForeignKey("mystery_box_prizes.id", ondelete="RESTRICT")
    )

    status: Mapped[MysteryBoxStatus] = mapped_column(
        enum_column(MysteryBoxStatus, "mystery_box_status"),
        default=MysteryBoxStatus.OPENED,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# =========================================================
# 14. DIRECTOR SOZLAMALARI
# =========================================================

class DirectorSetting(Base):
    __tablename__ = "director_settings"

    id: Mapped[int] = mapped_column(primary_key=True)

    key: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)
    value: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    updated_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# =========================================================
# 15. AUDIT JURNALI
# =========================================================

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT")
    )

    action: Mapped[str] = mapped_column(String(150), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str | None] = mapped_column(String(100))

    details: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    ip_address: Mapped[str | None] = mapped_column(String(64))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# =========================================================
# 16. INDEKSLAR
# =========================================================

Index("ix_products_status_created", Product.status, Product.created_at)
Index("ix_orders_customer_created", Order.customer_id, Order.created_at)
Index("ix_seller_orders_store_status", SellerOrder.store_id, SellerOrder.status)
Index("ix_reservations_status_expiry", StockReservation.status, StockReservation.expires_at)
Index("ix_audit_logs_created", AuditLog.created_at)
