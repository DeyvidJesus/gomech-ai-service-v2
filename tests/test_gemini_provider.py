from unittest.mock import MagicMock, patch

import pytest

from app.domain.schemas import ChatMessage, ChatRequest, DiagnosticRequest
from app.infrastructure.providers.factory import get_ai_provider
from app.infrastructure.providers.gemini_provider import GeminiProvider


@pytest.mark.asyncio
async def test_gemini_provider_factory():
    provider = get_ai_provider("gemini")
    assert isinstance(provider, GeminiProvider)
    assert provider.provider_name == "google-gemini-1.5-pro"


@pytest.mark.asyncio
async def test_gemini_provider_fallback_when_no_api_key():
    provider = GeminiProvider()
    provider.api_key = None

    req = ChatRequest(messages=[ChatMessage(role="user", content="Como calibrar a vela de ignição do Honda Civic?")])
    res = await provider.chat(req)

    assert res.reply is not None
    assert len(res.reply) > 0


@pytest.mark.asyncio
async def test_gemini_provider_chat_with_mocked_api():
    provider = GeminiProvider()
    provider.api_key = "AIzaSyTestKey123"

    mock_gemini_response = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "A folga correta das velas do Honda Civic é de 1.0mm a 1.1mm."}]
                }
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_gemini_response
    mock_response.raise_for_status.return_value = None

    with patch("httpx.AsyncClient.post", return_value=mock_response):
        req = ChatRequest(messages=[ChatMessage(role="user", content="Qual a folga da vela do Civic?")])
        res = await provider.chat(req)

        assert res.reply == "A folga correta das velas do Honda Civic é de 1.0mm a 1.1mm."
        assert res.usage.model_used == "gemini-1.5-flash"
        assert len(res.citations) > 0


@pytest.mark.asyncio
async def test_gemini_diagnose_capabilities():
    provider = GeminiProvider()
    req = DiagnosticRequest(
        symptoms_description="Ruído metálico na suspensão ao passar por lombadas",
        fault_codes=["C0035"]
    )
    res = await provider.diagnose(req)
    assert res is not None
    assert len(res.probable_causes) > 0
    assert len(res.recommended_inspection_steps) > 0
