from sqlmodel import Field, SQLModel
from datetime import datetime

class UserDB(SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    role: str = "user"
    created_at: datetime = Field(default_factory=datetime.utcnow)