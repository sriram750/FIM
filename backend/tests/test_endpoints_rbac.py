import pytest
from app.core.config import settings


@pytest.mark.asyncio
async def test_rbac_roles_login_and_permissions(client):
    # 1. Login as Analyst
    analyst_res = await client.post("/api/v1/auth/login", json={
        "email": "analyst@fim.local",
        "password": "Analyst@FIM2026!Secure",
    })
    assert analyst_res.status_code == 200
    analyst_data = analyst_res.json()
    assert analyst_data["user"]["role"] == "Analyst"
    assert "endpoints:read" in analyst_data["user"]["permissions"]
    assert "endpoints:manage" not in analyst_data["user"]["permissions"]

    # 2. Login as Auditor
    auditor_res = await client.post("/api/v1/auth/login", json={
        "email": "auditor@fim.local",
        "password": "Auditor@FIM2026!Secure",
    })
    assert auditor_res.status_code == 200
    auditor_data = auditor_res.json()
    assert auditor_data["user"]["role"] == "Auditor"
    assert "endpoints:read" in auditor_data["user"]["permissions"]
    assert "endpoints:manage" not in auditor_data["user"]["permissions"]


@pytest.mark.asyncio
async def test_endpoints_list_and_rbac_enforcement(client):
    # Admin Token
    admin_login = await client.post("/api/v1/auth/login", json={
        "email": settings.INITIAL_ADMIN_EMAIL,
        "password": settings.INITIAL_ADMIN_PASSWORD,
    })
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Auditor Token
    auditor_login = await client.post("/api/v1/auth/login", json={
        "email": "auditor@fim.local",
        "password": "Auditor@FIM2026!Secure",
    })
    auditor_token = auditor_login.json()["access_token"]
    auditor_headers = {"Authorization": f"Bearer {auditor_token}"}

    # 1. Anonymous access is blocked
    anon_resp = await client.get("/api/v1/endpoints")
    assert anon_resp.status_code == 401

    # 2. Both Admin and Auditor can read endpoints
    resp_admin = await client.get("/api/v1/endpoints", headers=admin_headers)
    assert resp_admin.status_code == 200
    assert "items" in resp_admin.json()

    resp_auditor = await client.get("/api/v1/endpoints", headers=auditor_headers)
    assert resp_auditor.status_code == 200
    assert "items" in resp_auditor.json()


@pytest.mark.asyncio
async def test_agent_installer_info_and_downloads(client):
    # 1. Fetch installer info
    info_resp = await client.get("/api/v1/agents/installer-info")
    assert info_resp.status_code == 200
    data = info_resp.json()
    assert "windows" in data
    assert "linux" in data
    assert "powershell_command" in data["windows"]
    assert "bash_command" in data["linux"]

    # 2. Windows standalone exe download
    exe_resp = await client.get("/api/v1/agents/download/windows-exe")
    assert exe_resp.status_code in [200, 404]

    # 3. Windows MSI download
    msi_resp = await client.get("/api/v1/agents/download/windows-msi")
    assert msi_resp.status_code in [200, 404]

    # 4. Linux script download
    sh_resp = await client.get("/api/v1/agents/download/linux-script")
    assert sh_resp.status_code in [200, 404]
