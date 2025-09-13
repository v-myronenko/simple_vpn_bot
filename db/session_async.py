import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

def _to_async(url: str) -> str:
    if url.startswith("sqlite:////"):
        return url.replace("sqlite:////", "sqlite+aiosqlite:////")
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://")
    return url

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////home/bot/data/vpn_users.db")
ASYNC_URL = _to_async(DATABASE_URL)

engine: AsyncEngine = create_async_engine(ASYNC_URL, echo=False, pool_pre_ping=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    return SessionLocal()
