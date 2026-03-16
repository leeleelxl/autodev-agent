import jwt
from pathlib import Path
from domain.interfaces import TokenSigner, TokenVerifier
from settings import settings
import stat

class RS256JWTImpl(TokenSigner, TokenVerifier):
    def __init__(self) -> None:
        self._validate_key_permissions(settings.jwt.private_key_path)
        with open(settings.jwt.private_key_path, "r") as f:
            self.priv = f.read()
        with open(settings.jwt.public_key_path, "r") as f:
            self.pub = f.read()

    @staticmethod
    def _validate_key_permissions(path: Path) -> None:
        st = path.stat()
        # 检查权限是否为 0o600
        if (st.st_mode & 0o777) != 0o600:
            raise RuntimeError(f"Private key {path} must have 600 permissions")

    def sign(self, payload: dict) -> str:
        return jwt.encode(
            payload,
            self.priv,
            algorithm=settings.jwt.alg,
            headers={"kid": "1"},
        )

    def verify(self, token: str) -> dict:
        return jwt.decode(
            token,
            self.pub,
            algorithms=[settings.jwt.alg],
            issuer=settings.jwt.issuer,
            options={"require": ["exp", "iss"]},
        )