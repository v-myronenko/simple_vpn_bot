from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    subscription_id: Mapped[int | None] = mapped_column(
        ForeignKey("subscriptions.id"), nullable=True
    )

    provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="telegram_stars"
    )
    amount_stars: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="XTR")

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending | success | failed | refunded

    provider_charge_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", backref="payments")
    subscription = relationship("Subscription", backref="payments")
