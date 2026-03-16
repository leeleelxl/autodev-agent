from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int | None = None
    username: str
    email: EmailStr
    password_hash: str
    role: str = "user"
    created_at: datetime