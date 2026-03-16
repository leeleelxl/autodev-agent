from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from settings import settings
from sqlmodel import SQLModel
import asyncio

engine = create_async_engine(settings.db_url, echo=False, future=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session