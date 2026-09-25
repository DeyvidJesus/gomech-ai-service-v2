from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient

from app.domain.exceptions import ProviderError, RateLimitError, TimeoutError
from app.main import app

client = TestClient(app)
AUTH_HEADERS = {
    "X-GoMech-Service-Auth": "gm-ai-internal-hmac-secret",
    "X-Tenant-Id": str(uuid4()),
}


@patch("app.application.services.ChatService.handle_chat")
def test_provider_rate_limit_handled(mock_handle_chat):
    mock_handle_chat.side_effect = RateLimitError("OpenAI quota exceeded", retry_after=10)

    response = client.post(
        "/api/v1/ai/chat",
        headers=AUTH_HEADERS,
        json={"messages": [{"role": "user", "content": "Olá"}]},
    )
    assert response.status_code == 429
    assert response.headers.get("retry-after") == "10"
    data = response.json()
    assert data["error_code"] == "AI_RATE_LIMIT"
    assert "OpenAI quota exceeded" in data["detail"]


@patch("app.application.services.DiagnosticService.handle_diagnosis")
def test_provider_timeout_handled(mock_handle_diag):
    mock_handle_diag.side_effect = TimeoutError("Provider connection timed out")

    response = client.post(
        "/api/v1/ai/diagnose",
        headers=AUTH_HEADERS,
        json={"symptoms_description": "Barulho de vibração no cardan"},
    )
    assert response.status_code == 504
    data = response.json()
    assert data["error_code"] == "AI_TIMEOUT"
    assert "timed out" in data["detail"]


@patch("app.application.services.QuoteService.handle_quote_generation")
def test_provider_generic_error_handled(mock_handle_quote):
    mock_handle_quote.side_effect = ProviderError("External upstream API 500", status_code=502)

    response = client.post(
        "/api/v1/ai/generate-quote-items",
        headers=AUTH_HEADERS,
        json={
            "vehicle_info": "Fiat Uno",
            "diagnostic_summary": "Troca de pastilhas de freio",
        },
    )
    assert response.status_code == 502
    data = response.json()
    assert data["error_code"] == "AI_PROVIDER_ERROR"
