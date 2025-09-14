# db/models.py
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Index,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

# ---------------------------------------------------------------------
# env + engine
# ---------------------------------------------------------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # fallback для локалки (щоб не впав, якщо .env ще не зроблений)
    DATABASE_URL = "sqlite+aiosqlite:///./local.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


# ---------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------
def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------
# models
# ---------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    starts_at = Column(DateTime, default=utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_trial = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    user = relationship("User", back_populates="subscriptions")


# ---------------------------------------------------------------------
# create tables (на випадок першого запуску)
# ---------------------------------------------------------------------
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
