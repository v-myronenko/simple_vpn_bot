# db/models.py
from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from dotenv import load_dotenv

def _resolve_database_url() -> str:
    """Return an async-capable database URL.

    Falls back to a local SQLite database when ``DATABASE_URL`` is not set and
    upgrades any synchronous SQLite URLs to their async variant. This keeps the
    development experience simple while still surfacing a clear error for other
    backends that are misconfigured.
    """

    raw_url = os.getenv("DATABASE_URL")
    if not raw_url:
        return "sqlite+aiosqlite:///./local.db"

    url = make_url(raw_url)
    backend = url.get_backend_name()
    driver = url.drivername

    if backend == "sqlite" and "aiosqlite" not in driver:
        # Accept common synchronous variants such as ``sqlite:///`` and
        # ``sqlite+pysqlite://`` by transparently upgrading them to the async
        # driver expected by ``create_async_engine``.
        upgraded = url.set(drivername="sqlite+aiosqlite")
        return upgraded.render_as_string(hide_password=False)

    if "+" not in driver:
        raise RuntimeError(
            "DATABASE_URL must use an async driver (e.g. 'postgresql+asyncpg://', "
            "'mysql+aiomysql://'). Got driver %r in %r" % (driver, raw_url)
        )

    return raw_url


load_dotenv()
DATABASE_URL = _resolve_database_url()

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    # важливо: timezone=True
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    subscriptions = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # важливо: timezone=True
    starts_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_trial = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    user = relationship("User", back_populates="subscriptions")


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
