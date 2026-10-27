import pytest
from app.core.config import settings


@pytest.mark.asyncio
async def test_auth_login_success(client):
    payload = {
        "email": settings.INITIAL_ADMIN_EMAIL,
        "password": settings.INITIAL_ADMIN_PASSWORD,
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == settings.INITIAL_ADMIN_EMAIL
    assert data["user"]["is_superuser"] is True


@pytest.mark.asyncio
async def test_auth_login_invalid_password(client):
    payload = {
        "email": settings.INITIAL_ADMIN_EMAIL,
        "password": "WrongPassword123!",
    }
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_auth_get_me(client):
    # First login
    payload = {
        "email": settings.INITIAL_ADMIN_EMAIL,
        "password": settings.INITIAL_ADMIN_PASSWORD,
    }
    login_resp = await client.post("/api/v1/auth/login", json=payload)
    token = login_resp.json()["access_token"]

    # Call /auth/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == settings.INITIAL_ADMIN_EMAIL
    assert me_data["role"] == "Admin"


@pytest.mark.asyncio
async def test_auth_unauthorized_access(client):
    me_resp = await client.get("/api/v1/auth/me")
    assert me_resp.status_code == 401
