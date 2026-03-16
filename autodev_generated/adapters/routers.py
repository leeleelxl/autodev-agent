from fastapi import APIRouter, Depends, status
from pydantic import EmailStr, BaseModel
from datetime import datetime, timezone
from domain.use_cases import RegisterUser, AuthenticateUser
from domain.interfaces import UserRepository
from adapters.deps import get_session_repo, get_current_user
from adapters.jwt_rs256 import RS256JWTImpl
from adapters.database import init_db
from typing import Annotated

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class RegisterResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int

@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    repo: Annotated[UserRepository, Depends(get_session_repo)],
) -> RegisterResponse:
    await init_db()  # 确保表已创建
    uc = RegisterUser(repo)
    user = await uc.execute(body.username, body.email, body.password)
    return RegisterResponse(**user.model_dump())

@router.post("/auth/login")
async def login(
    body: LoginRequest,
    repo: Annotated[UserRepository, Depends(get_session_repo)],
) -> LoginResponse:
    await init_db()
    uc = AuthenticateUser(repo)
    user = await uc.execute(body.username, body.password)
    signer = RS256JWTImpl()
    now = datetime.now(timezone.utc)
    exp = int((now).timestamp()) + settings.jwt.exp_seconds
    token = signer.sign({"uid": user.id, "role": user.role, "exp": exp, "iss": settings.jwt.issuer})
    return LoginResponse(access_token=token, expires_in=settings.jwt.exp_seconds)

@router.get("/auth/me")
async def me(current: Annotated[User, Depends(get_current_user)]):
    return current.model_dump()