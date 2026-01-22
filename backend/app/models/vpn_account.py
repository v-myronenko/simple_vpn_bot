from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VPNAccount(Base):
    __tablename__ = "vpn_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    server_id: Mapped[int] = mapped_column(ForeignKey("servers.id"), nullable=False)

    protocol: Mapped[str] = mapped_column(
        String(50), nullable=False, default="vless_reality"
    )
    uuid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    external_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # id у панелі x-ui, якщо є

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    user = relationship("User", backref="vpn_accounts")
    server = relationship("Server", backref="vpn_accounts")
