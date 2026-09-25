from abc import ABC, abstractmethod

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


class AiProvider(ABC):
    """Abstract base provider ensuring interchangeable LLM and AI models."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        pass

    @abstractmethod
    async def diagnose(self, request: DiagnosticRequest) -> DiagnosticResponse:
        pass

    @abstractmethod
    async def recommend_parts(self, request: PartsRecommendationRequest) -> PartsRecommendationResponse:
        pass

    @abstractmethod
    async def recommend_maintenance(self, request: MaintenanceRecommendationRequest) -> MaintenanceRecommendationResponse:
        pass

    @abstractmethod
    async def assist_mechanic(self, request: MechanicAssistRequest) -> MechanicAssistResponse:
        pass

    @abstractmethod
    async def search_video(self, request: VideoSearchRequest) -> VideoSearchResponse:
        pass

    @abstractmethod
    async def extract_document(self, request: DocumentExtractionRequest) -> DocumentExtractionResponse:
        pass

    @abstractmethod
    async def draft_message(self, request: CustomerMessageDraftRequest) -> CustomerMessageDraftResponse:
        pass

    @abstractmethod
    async def generate_quote(self, request: QuoteGenerationRequest) -> QuoteProposalResponse:
        pass

    @abstractmethod
    async def summarize_work_order(self, request: WorkOrderSummaryRequest) -> WorkOrderSummaryResponse:
        pass

    @abstractmethod
    async def generate_insights(self, request: AnalyticsInsightsRequest) -> AnalyticsInsightsResponse:
        pass
