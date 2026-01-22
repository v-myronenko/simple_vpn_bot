from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Server(Base):
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    region: Mapped[str] = mapped_column(String(20))
    provider_type: Mapped[str] = mapped_column(String(50))  # xray_vless_reality
    api_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    api_user: Mapped[str | None] = mapped_column(String(100), nullable=True)
    api_password: Mapped[str | None] = mapped_column(String(100), nullable=True)
    api_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
