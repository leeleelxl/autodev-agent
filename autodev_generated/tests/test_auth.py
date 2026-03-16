import pytest
from httpx import AsyncClient
from app import app

@pytest.mark.asyncio
async def test_register_login_flow():
    async with AsyncClient(app=app, base_url="http://test") as c:
        # 注册
        r = await c.post("/auth/register", json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "Super@123"
        })
        assert r.status_code == 201
        uid = r.json()["id"]
        # 登录
        r = await c.post("/auth/login", json={
            "username": "alice",
            "password": "Super@123"
        })
        assert r.status_code == 200
        token = r.json()["access_token"]
        # 访问受保护资源
        r = await c.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["id"] == uid