import asyncio

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
    MaintenanceRecommendationRequest,
    MaintenanceRecommendationResponse,
    MechanicAssistRequest,
    MechanicAssistResponse,
    PartsRecommendationRequest,
    PartsRecommendationResponse,
    QuoteGenerationRequest,
    QuoteProposalResponse,
    VideoSearchRequest,
    VideoSearchResponse,
    WorkOrderSummaryRequest,
    WorkOrderSummaryResponse,
)
from app.infrastructure.providers.base import AiProvider
from app.infrastructure.providers.mock_provider import MockAiProvider


class OpenAIProvider(AiProvider):
    """OpenAI adapter skeleton with bounded retries, timeout mapping, and fallback.

    The retry and error-translation path is in place, but no OpenAI API call is wired yet:
    every capability currently delegates to the fallback provider.
    """

    def __init__(self, fallback_provider: AiProvider | None = None):
        self.fallback = fallback_provider or MockAiProvider()
        self.api_key = settings.OPENAI_API_KEY
        self.base_url = settings.OPENAI_BASE_URL
        self.timeout = settings.TIMEOUT_SECONDS
        self.max_retries = settings.MAX_RETRIES

    @property
    def provider_name(self) -> str:
        return "openai-gpt4o"

    async def _execute_with_retry(self, operation_name: str, coro_fn):
        if not self.api_key:
            # Fallback when no live API key is provisioned
            return await coro_fn(use_fallback=True)

        for attempt in range(1, self.max_retries + 1):
            try:
                return await coro_fn(use_fallback=False)
            except httpx.TimeoutException as te:
                if attempt == self.max_retries:
                    raise TimeoutError(f"OpenAI API call timed out after {self.max_retries} attempts") from te
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))
            except httpx.HTTPStatusError as he:
                if he.response.status_code == 429:
                    if attempt == self.max_retries:
                        raise RateLimitError("OpenAI rate limit exceeded", retry_after=5) from he
                    await asyncio.sleep(0.2 * (2 ** (attempt - 1)))
                elif attempt == self.max_retries:
                    raise ProviderError(f"OpenAI HTTP error {he.response.status_code}: {he.response.text}") from he
            except Exception as e:
                if attempt == self.max_retries:
                    raise ProviderError(f"OpenAI invocation failed: {str(e)}") from e
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

    async def chat(self, request: ChatRequest) -> ChatResponse:
        async def _call(use_fallback: bool):
            return await self.fallback.chat(request)

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
