from datetime import datetime, timezone
from domain.entities import User
from domain.interfaces import UserRepository, TokenSigner
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=1)

class RegisterUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, username: str, email: str, raw_pwd: str) -> User:
        if await self.repo.find_by_username(username):
            raise ValueError("USERNAME_EXISTS")
        if await self.repo.find_by_email(email):
            raise ValueError("EMAIL_EXISTS")
        pwd_hash = ph.hash(raw_pwd)
        user = User(
            username=username,
            email=email,
            password_hash=pwd_hash,
            created_at=datetime.now(timezone.utc),
        )
        return await self.repo.save(user)

class AuthenticateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def execute(self, username: str, raw_pwd: str) -> User:
        user = await self.repo.find_by_username(username)
        if not user:
            raise ValueError("INVALID_CREDENTIALS")
        try:
            ph.verify(user.password_hash, raw_pwd)
        except VerifyMismatchError:
            raise ValueError("INVALID_CREDENTIALS")
        return user

class ValidateToken:
    def __init__(self, verifier: TokenVerifier):
        self.verifier = verifier

    def execute(self, token: str) -> dict:
        return self.verifier.verify(token)