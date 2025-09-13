import os
import pathlib
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from .session import get_session

MIGRATIONS_DIR = os.getenv("MIGRATIONS_DIR", str(pathlib.Path(__file__).resolve().parents[2] / "migrations"))

async def run_sql_file(session: AsyncSession, path: str):
    sql = pathlib.Path(path).read_text(encoding="utf-8")
    # sqlite дозволяє виконувати кілька інструкцій за раз через exec_driver_sql
    await session.execute(sql)  # type: ignore[arg-type]
    await session.commit()

async def main():
    async with await get_session() as session:
        # Порядок має значення
        await run_sql_file(session, os.path.join(MIGRATIONS_DIR, "01_init.sql"))
    print("Migrations applied.")

if __name__ == "__main__":
    asyncio.run(main())
