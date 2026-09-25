import time

from app.core.observability import (
    AI_REQUEST_LATENCY,
    AI_REQUESTS_TOTAL,
    AI_TOKENS_TOTAL,
    logger,
)
from app.core.security import ServiceContext
from app.domain.guardrails import check_safety_guardrails, sanitize_sensitive_data
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
from app.infrastructure.providers.factory import get_ai_provider


class ChatService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_chat(self, ctx: ServiceContext, request: ChatRequest) -> ChatResponse:
        start = time.perf_counter()
        capability = "CHAT"
        provider_name = self.provider.provider_name

        try:
            # Validate input and redact personal data before calling a provider.
            for msg in request.messages:
                check_safety_guardrails(msg.content)
                msg.content = sanitize_sensitive_data(msg.content)

            # Call the configured provider.
            response = await self.provider.chat(request)

            # Reject unsafe provider output.
            check_safety_guardrails(response.reply)

            # Record usage and latency.
            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            AI_TOKENS_TOTAL.labels(capability=capability, type="prompt").inc(response.usage.prompt_tokens)
            AI_TOKENS_TOTAL.labels(capability=capability, type="completion").inc(response.usage.completion_tokens)

            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Chat service failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise


class DiagnosticService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_diagnosis(self, ctx: ServiceContext, request: DiagnosticRequest) -> DiagnosticResponse:
        start = time.perf_counter()
        capability = "DIAGNOSTIC_ASSIST"
        provider_name = self.provider.provider_name

        try:
            check_safety_guardrails(request.symptoms_description)
            request.symptoms_description = sanitize_sensitive_data(request.symptoms_description)
            if request.customer_notes:
                check_safety_guardrails(request.customer_notes)
                request.customer_notes = sanitize_sensitive_data(request.customer_notes)

            response = await self.provider.diagnose(request)

            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            AI_TOKENS_TOTAL.labels(capability=capability, type="prompt").inc(response.usage.prompt_tokens)
            AI_TOKENS_TOTAL.labels(capability=capability, type="completion").inc(response.usage.completion_tokens)

            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Diagnosis service failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise


class RecommendationService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_parts_recommendation(
        self, ctx: ServiceContext, request: PartsRecommendationRequest
    ) -> PartsRecommendationResponse:
        start = time.perf_counter()
        capability = "PARTS_RECOMMENDATION"
        provider_name = self.provider.provider_name

        try:
            if request.reported_symptoms:
                check_safety_guardrails(request.reported_symptoms)
                request.reported_symptoms = sanitize_sensitive_data(request.reported_symptoms)

            response = await self.provider.recommend_parts(request)

            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            AI_TOKENS_TOTAL.labels(capability=capability, type="prompt").inc(response.usage.prompt_tokens)
            AI_TOKENS_TOTAL.labels(capability=capability, type="completion").inc(response.usage.completion_tokens)

            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Parts recommendation failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise

    async def handle_maintenance_recommendation(
        self, ctx: ServiceContext, request: MaintenanceRecommendationRequest
    ) -> MaintenanceRecommendationResponse:
        start = time.perf_counter()
        capability = "MAINTENANCE_RECOMMENDATION"
        provider_name = self.provider.provider_name

        try:
            response = await self.provider.recommend_maintenance(request)

            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            AI_TOKENS_TOTAL.labels(capability=capability, type="prompt").inc(response.usage.prompt_tokens)
            AI_TOKENS_TOTAL.labels(capability=capability, type="completion").inc(response.usage.completion_tokens)

            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Maintenance recommendation failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise


class MechanicAssistanceService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_mechanic_assist(
        self, ctx: ServiceContext, request: MechanicAssistRequest
    ) -> MechanicAssistResponse:
        start = time.perf_counter()
        capability = "MECHANIC_ASSIST"
        provider_name = self.provider.provider_name

        try:
            check_safety_guardrails(request.question_or_procedure)
            response = await self.provider.assist_mechanic(request)

            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Mechanic assist failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise


class VideoSearchService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_video_search(
        self, ctx: ServiceContext, request: VideoSearchRequest
    ) -> VideoSearchResponse:
        start = time.perf_counter()
        capability = "VIDEO_SEARCH"
        provider_name = self.provider.provider_name

        try:
            response = await self.provider.search_video(request)
            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Video search failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise


class DocumentExtractionService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_extraction(
        self, ctx: ServiceContext, request: DocumentExtractionRequest
    ) -> DocumentExtractionResponse:
        start = time.perf_counter()
        capability = "DOCUMENT_EXTRACTION"
        provider_name = self.provider.provider_name

        try:
            response = await self.provider.extract_document(request)
            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Document extraction failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise


class CommunicationService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_draft_message(
        self, ctx: ServiceContext, request: CustomerMessageDraftRequest
    ) -> CustomerMessageDraftResponse:
        start = time.perf_counter()
        capability = "CUSTOMER_MESSAGE_DRAFT"
        provider_name = self.provider.provider_name

        try:
            request.customer_name = sanitize_sensitive_data(request.customer_name)
            if request.key_details:
                request.key_details = sanitize_sensitive_data(request.key_details)

            response = await self.provider.draft_message(request)
            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Message draft failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise


class QuoteService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_quote_generation(
        self, ctx: ServiceContext, request: QuoteGenerationRequest
    ) -> QuoteProposalResponse:
        start = time.perf_counter()
        capability = "QUOTE_GENERATION"
        provider_name = self.provider.provider_name

        try:
            check_safety_guardrails(request.diagnostic_summary)
            request.diagnostic_summary = sanitize_sensitive_data(request.diagnostic_summary)

            response = await self.provider.generate_quote(request)
            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Quote generation failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise


class WorkOrderSummaryService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_summary(
        self, ctx: ServiceContext, request: WorkOrderSummaryRequest
    ) -> WorkOrderSummaryResponse:
        start = time.perf_counter()
        capability = "WORK_ORDER_SUMMARY"
        provider_name = self.provider.provider_name

        try:
            request.customer_reported_issues = sanitize_sensitive_data(request.customer_reported_issues)
            if request.mechanic_notes:
                request.mechanic_notes = sanitize_sensitive_data(request.mechanic_notes)

            response = await self.provider.summarize_work_order(request)
            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Work order summary failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise


class AnalyticsInsightsService:
    def __init__(self):
        self.provider = get_ai_provider()

    async def handle_insights(
        self, ctx: ServiceContext, request: AnalyticsInsightsRequest
    ) -> AnalyticsInsightsResponse:
        start = time.perf_counter()
        capability = "ANALYTICS_INSIGHTS"
        provider_name = self.provider.provider_name

        try:
            response = await self.provider.generate_insights(request)
            duration = time.perf_counter() - start
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="SUCCESS").inc()
            AI_REQUEST_LATENCY.labels(capability=capability, provider=provider_name).observe(duration)
            return response
        except Exception as e:
            AI_REQUESTS_TOTAL.labels(capability=capability, provider=provider_name, status="FAILED").inc()
            logger.error(f"Analytics insights failure: {str(e)}", extra={"tenant_id": str(ctx.tenant_id), "capability": capability})
            raise
