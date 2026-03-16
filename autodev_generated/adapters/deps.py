from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from domain.use_cases import ValidateToken
from adapters.jwt_rs256 import RS256JWTImpl
from domain.interfaces import UserRepository
from domain.entities import User
from adapters.repository_sqlite import SQLiteUserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from adapters.database import get_session
from typing import Annotated

security = HTTPBearer()

async def get_session_repo(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return SQLiteUserRepository(session)

async def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(security),
    repo: UserRepository = Depends(get_session_repo),
) -> User:
    verifier = RS256JWTImpl()
    uc = ValidateToken(verifier)
    try:
        payload = uc.execute(cred.credentials)
        uid: int = payload["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")
    user = await repo.find_by_id(uid)   # 修复：使用 find_by_id 而非 find_by_username
    if not user:
        raise HTTPException(status_code=401, detail="USER_NOT_FOUND")
    return user