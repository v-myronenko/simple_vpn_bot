import os, pathlib, asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from .session_async import get_session

MIGRATIONS_DIR = os.getenv("MIGRATIONS_DIR", str(pathlib.Path(__file__).resolve().parents[1] / "migrations"))

async def run_sql_file(session: AsyncSession, path: str):
    sql = pathlib.Path(path).read_text(encoding="utf-8")
    await session.execute(sql)  # sqlite приймає multi-stmt
    await session.commit()

async def main():
    async with await get_session() as session:
        await run_sql_file(session, os.path.join(MIGRATIONS_DIR, "01_init.sql"))
    print("Migrations applied.")

if __name__ == "__main__":
    asyncio.run(main())
