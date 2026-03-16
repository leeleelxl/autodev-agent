from pydantic import BaseModel, EmailStr
from pydantic_settings import BaseSettings   # 修复：导入缺失
from pathlib import Path
import tempfile
import os

class _JWTSettings(BaseModel):
    alg: str = "RS256"
    private_key_path: Path = Path(tempfile.gettempdir()) / "jwtRS256.key"
    public_key_path: Path = Path(tempfile.gettempdir()) / "jwtRS256.key.pub"
    exp_seconds: int = 60 * 60 * 24 * 7  # 7 天
    issuer: str = "auth-service"

class Settings(BaseSettings):
    app_name: str = "CleanAuth"
    db_url: str = "sqlite+aiosqlite:///./auth.db"
    jwt: _JWTSettings = _JWTSettings()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

settings = Settings()