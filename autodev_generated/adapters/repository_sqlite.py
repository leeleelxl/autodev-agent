from sqlmodel import Field, SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from domain.interfaces import UserRepository
from domain.entities import User as UserEntity
from adapters.models import UserDB
from typing import Any

class SQLiteUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.s = session

    async def save(self, user: UserEntity) -> UserEntity:
        db_user = UserDB(**user.model_dump(exclude={"id"}))
        self.s.add(db_user)
        await self.s.commit()
        await self.s.refresh(db_user)
        return UserEntity(**db_user.model_dump())

    async def find_by_username(self, username: str) -> UserEntity | None:
        stmt = select(UserDB).where(UserDB.username == username)
        res = await self.s.execute(stmt)
        obj = res.scalar_one_or_none()
        return UserEntity(**obj.model_dump()) if obj else None

    async def find_by_email(self, email: str) -> UserEntity | None:
        stmt = select(UserDB).where(UserDB.email == email)
        res = await self.s.execute(stmt)
        obj = res.scalar_one_or_none()
        return UserEntity(**obj.model_dump()) if obj else None

    async def find_by_id(self, uid: int) -> UserEntity | None:   # 新增：修复高优问题
        stmt = select(UserDB).where(UserDB.id == uid)
        res = await self.s.execute(stmt)
        obj = res.scalar_one_or_none()
        return UserEntity(**obj.model_dump()) if obj else None