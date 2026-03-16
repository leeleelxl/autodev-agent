from abc import ABC, abstractmethod
from domain.entities import User

class UserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def find_by_username(self, username: str) -> User | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> User | None: ...

    @abstractmethod
    async def find_by_id(self, uid: int) -> User | None: ...  # 新增：修复高优问题

class TokenSigner(ABC):
    @abstractmethod
    def sign(self, payload: dict) -> str: ...

class TokenVerifier(ABC):
    @abstractmethod
    def verify(self, token: str) -> dict: ...