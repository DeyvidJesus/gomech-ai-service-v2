from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
VALID_AUTH_SECRET = "gm-ai-local-dev-secret"


def test_missing_auth_header_rejected():
    response = client.post(
        "/api/v1/ai/chat",
        json={"messages": [{"role": "user", "content": "Olá"}]},
    )
    assert response.status_code == 401
    assert "Unauthorized" in response.json()["detail"]


def test_invalid_auth_secret_rejected():
    response = client.post(
        "/api/v1/ai/chat",
        headers={
            "X-GoMech-Service-Auth": "wrong-secret",
            "X-Tenant-Id": str(uuid4()),
        },
        json={"messages": [{"role": "user", "content": "Olá"}]},
    )
    assert response.status_code == 401


def test_missing_tenant_id_rejected():
    response = client.post(
        "/api/v1/ai/chat",
        headers={
            "X-GoMech-Service-Auth": VALID_AUTH_SECRET,
        },
        json={"messages": [{"role": "user", "content": "Olá"}]},
    )
    assert response.status_code == 400
    assert "X-Tenant-Id" in response.json()["detail"]


def test_invalid_tenant_uuid_rejected():
    response = client.post(
        "/api/v1/ai/chat",
        headers={
            "X-GoMech-Service-Auth": VALID_AUTH_SECRET,
            "X-Tenant-Id": "not-a-uuid",
        },
        json={"messages": [{"role": "user", "content": "Olá"}]},
    )
    assert response.status_code == 400
    assert "valid UUID" in response.json()["detail"]


def test_valid_auth_and_tenant_accepted():
    tenant_id = str(uuid4())
    response = client.post(
        "/api/v1/ai/chat",
        headers={
            "X-GoMech-Service-Auth": VALID_AUTH_SECRET,
            "X-Tenant-Id": tenant_id,
            "X-User-Id": str(uuid4()),
            "X-Correlation-Id": "corr-test-123",
        },
        json={"messages": [{"role": "user", "content": "Como testar a bobina?"}]},
    )
    assert response.status_code == 200
    assert "reply" in response.json()
    assert response.json()["usage"]["total_tokens"] > 0
