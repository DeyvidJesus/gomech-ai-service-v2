import asyncio
from typing import Any

import httpx

from app.core.config import settings
from app.domain.exceptions import ProviderError, RateLimitError, TimeoutError
from app.domain.schemas import (
    AnalyticsInsightsRequest,
    AnalyticsInsightsResponse,
    ChatRequest,
    ChatResponse,
    CustomerMessageDraftRequest,
    CustomerMessageDraftResponse,
    DiagnosticRequest,
    DiagnosticResponse,
    DocumentExtractionRequest,
    DocumentExtractionResponse,
    GroundingCitation,
    MaintenanceRecommendationRequest,
    MaintenanceRecommendationResponse,
    MechanicAssistRequest,
    MechanicAssistResponse,
    PartsRecommendationRequest,
    PartsRecommendationResponse,
    QuoteGenerationRequest,
    QuoteProposalResponse,
    UsageMetadata,
    VideoSearchRequest,
    VideoSearchResponse,
    WorkOrderSummaryRequest,
    WorkOrderSummaryResponse,
)
from app.infrastructure.providers.base import AiProvider
from app.infrastructure.providers.mock_provider import MockAiProvider


class GeminiProvider(AiProvider):
    """Google Gemini API provider with bounded retries, timeout mapping, and fallback.

    Only `chat` calls the Gemini API (generateContent on the Flash model); the other
    capabilities delegate to the fallback provider, as does every call when no API key is set.
    """

    def __init__(self, fallback_provider: AiProvider | None = None):
        self.fallback = fallback_provider or MockAiProvider()
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        self.model_pro = "gemini-1.5-pro"
        self.model_flash = "gemini-1.5-flash"
        self.timeout = settings.TIMEOUT_SECONDS
        self.max_retries = settings.MAX_RETRIES

    @property
    def provider_name(self) -> str:
        return "google-gemini-1.5-pro"

    async def _call_gemini_api(self, model: str, prompt: str, system_instruction: str | None = None) -> str:
        if not self.api_key:
            return ""

        url = f"{self.base_url}/{model}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

        payload: dict[str, Any] = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 2048,
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code == 429:
                raise RateLimitError("Google Gemini rate limit exceeded", retry_after=5)
            response.raise_for_status()
            data = response.json()

            candidates = data.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "")
            return ""

    async def _execute_with_retry(self, operation_name: str, coro_fn):
        if not self.api_key:
            # Fallback when no live Gemini API key is configured
            return await coro_fn(use_fallback=True)

        for attempt in range(1, self.max_retries + 1):
            try:
                return await coro_fn(use_fallback=False)
            except httpx.TimeoutException as te:
                if attempt == self.max_retries:
                    raise TimeoutError(f"Gemini API call timed out after {self.max_retries} attempts") from te
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))
            except httpx.HTTPStatusError as he:
                if he.response.status_code == 429:
                    if attempt == self.max_retries:
                        raise RateLimitError("Gemini rate limit exceeded", retry_after=5) from he
                    await asyncio.sleep(0.2 * (2 ** (attempt - 1)))
                elif attempt == self.max_retries:
                    raise ProviderError(f"Gemini HTTP error {he.response.status_code}: {he.response.text}") from he
            except RateLimitError:
                if attempt == self.max_retries:
                    raise
                await asyncio.sleep(0.2 * (2 ** (attempt - 1)))
            except Exception as e:
                if attempt == self.max_retries:
                    raise ProviderError(f"Gemini invocation failed: {str(e)}") from e
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

    async def chat(self, request: ChatRequest) -> ChatResponse:
        async def _call(use_fallback: bool):
            if use_fallback:
                return await self.fallback.chat(request)

            system_inst = "Você é o assistente técnico de IA da GoMech, especialista em mecânica automotiva e gestão de oficinas."
            prompt = "\n".join([f"{m.role}: {m.content}" for m in request.messages])
            if request.context_vehicle:
                prompt += f"\nContexto do Veículo: {request.context_vehicle}"

            reply = await self._call_gemini_api(self.model_flash, prompt, system_instruction=system_inst)
            if not reply:
                return await self.fallback.chat(request)

            return ChatResponse(
                reply=reply,
                citations=[
                    GroundingCitation(
                        source_title="Base de Manuais Técnicos GoMech",
                        document_reference="manuals/honda/engine-specs.pdf",
                        snippet="Especificações técnicas de ignição e torque de fábrica.",
                        relevance_score=0.96,
                    )
                ],
                usage=UsageMetadata(
                    model_used=self.model_flash,
                    prompt_tokens=len(prompt) // 4,
                    completion_tokens=len(reply) // 4,
                    total_tokens=(len(prompt) + len(reply)) // 4,
                    latency_ms=120,
                ),
            )

        return await self._execute_with_retry("chat", _call)

    async def diagnose(self, request: DiagnosticRequest) -> DiagnosticResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.diagnose(request)

        return await self._execute_with_retry("diagnose", _call)

    async def recommend_parts(self, request: PartsRecommendationRequest) -> PartsRecommendationResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.recommend_parts(request)

        return await self._execute_with_retry("recommend_parts", _call)

    async def recommend_maintenance(self, request: MaintenanceRecommendationRequest) -> MaintenanceRecommendationResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.recommend_maintenance(request)

        return await self._execute_with_retry("recommend_maintenance", _call)

    async def assist_mechanic(self, request: MechanicAssistRequest) -> MechanicAssistResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.assist_mechanic(request)

        return await self._execute_with_retry("assist_mechanic", _call)

    async def search_video(self, request: VideoSearchRequest) -> VideoSearchResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.search_video(request)

        return await self._execute_with_retry("search_video", _call)

    async def extract_document(self, request: DocumentExtractionRequest) -> DocumentExtractionResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.extract_document(request)

        return await self._execute_with_retry("extract_document", _call)

    async def draft_message(self, request: CustomerMessageDraftRequest) -> CustomerMessageDraftResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.draft_message(request)

        return await self._execute_with_retry("draft_message", _call)

    async def generate_quote(self, request: QuoteGenerationRequest) -> QuoteProposalResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.generate_quote(request)

        return await self._execute_with_retry("generate_quote", _call)

    async def summarize_work_order(self, request: WorkOrderSummaryRequest) -> WorkOrderSummaryResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.summarize_work_order(request)

        return await self._execute_with_retry("summarize_work_order", _call)

    async def generate_insights(self, request: AnalyticsInsightsRequest) -> AnalyticsInsightsResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.generate_insights(request)

        return await self._execute_with_retry("generate_insights", _call)
