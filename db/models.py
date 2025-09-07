from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta
import enum
from .base import Base

class SubStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"
    PENDING = "pending"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lang: Mapped[str | None] = mapped_column(String(8), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user")
    payments: Mapped[list["Payment"]] = relationship(back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[SubStatus] = mapped_column(Enum(SubStatus), default=SubStatus.ACTIVE)
    plan: Mapped[str] = mapped_column(String(32), default="monthly")
    server_location: Mapped[str | None] = mapped_column(String(32))
    uuid: Mapped[str | None] = mapped_column(String(64))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.utcnow() + timedelta(days=31))

    user: Mapped["User"] = relationship(back_populates="subscriptions")

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider: Mapped[str] = mapped_column(String(32))
    amount: Mapped[int] = mapped_column(Integer)
    reference: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    meta: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="payments")

    __table_args__ = (UniqueConstraint("reference", name="uix_payment_reference"),)
