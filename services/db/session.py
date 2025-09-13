import os
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession

# DATABASE_URL у .env: sqlite:////home/bot/data/vpn_users.db
# Для async драйвера sqlite треба префікс sqlite+aiosqlite:///
def _to_async_url(url: str) -> str:
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
    if url.startswith("sqlite:////"):  # абсолютний шлях
        return url.replace("sqlite:////", "sqlite+aiosqlite:////")
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://")
    return url  # інші СУБД (postgresql+asyncpg тощо) як є

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////home/bot/data/vpn_users.db")
ASYNC_DB_URL = _to_async_url(DATABASE_URL)

engine: AsyncEngine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    pool_pre_ping=True,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    return SessionLocal()
