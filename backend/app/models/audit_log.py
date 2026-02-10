from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    # Хто
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger, nullable=True, index=True
    )

    # Звідки
    source: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # backend | bot | script

    # Що сталося
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # payment.telegram_stars.completed etc.
    level: Mapped[str] = mapped_column(
        String(10), nullable=False, default="info"
    )  # info | warning | error

    # До чого відноситься (не обов'язково)
    object_type: Mapped[str | None] = mapped_column(
        String(30), nullable=True
    )  # subscription | payment | trial | vpn_account
    object_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    description: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    # JSON-метадані (серіалізовані в текст)
    meta: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", backref="audit_logs")
