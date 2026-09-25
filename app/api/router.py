from fastapi import APIRouter, Depends, Response

from app.application.services import (
    AnalyticsInsightsService,
    ChatService,
    CommunicationService,
    DiagnosticService,
    DocumentExtractionService,
    MechanicAssistanceService,
    QuoteService,
    RecommendationService,
    VideoSearchService,
    WorkOrderSummaryService,
)
from app.core.observability import get_metrics_data
from app.core.security import ServiceContext, verify_service_auth
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

api_router = APIRouter(prefix="/api/v1/ai")
health_router = APIRouter()

chat_service = ChatService()
diag_service = DiagnosticService()
rec_service = RecommendationService()
mech_service = MechanicAssistanceService()
video_service = VideoSearchService()
extract_service = DocumentExtractionService()
comm_service = CommunicationService()
quote_service = QuoteService()
summary_service = WorkOrderSummaryService()
analytics_service = AnalyticsInsightsService()

@health_router.get("/")
def root():
    return {"service": "gomech-ai", "status": "ok", "version": "1.0.0"}

@health_router.get("/health")
def health():
    return {"status": "ok", "database_connected": False, "mode": "stateless-isolated"}

@health_router.get("/metrics")
def metrics():
    data, content_type = get_metrics_data()
    return Response(content=data, media_type=content_type)

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, ctx: ServiceContext = Depends(verify_service_auth)):
    return await chat_service.handle_chat(ctx, request)

@api_router.post("/diagnose", response_model=DiagnosticResponse)
async def diagnose(request: DiagnosticRequest, ctx: ServiceContext = Depends(verify_service_auth)):
    return await diag_service.handle_diagnosis(ctx, request)

@api_router.post("/recommendations/parts", response_model=PartsRecommendationResponse)
async def recommend_parts(
    request: PartsRecommendationRequest, ctx: ServiceContext = Depends(verify_service_auth)
):
    return await rec_service.handle_parts_recommendation(ctx, request)

@api_router.post("/recommendations/maintenance", response_model=MaintenanceRecommendationResponse)
async def recommend_maintenance(
    request: MaintenanceRecommendationRequest, ctx: ServiceContext = Depends(verify_service_auth)
):
    return await rec_service.handle_maintenance_recommendation(ctx, request)

@api_router.post("/mechanic-assist", response_model=MechanicAssistResponse)
async def mechanic_assist(
    request: MechanicAssistRequest, ctx: ServiceContext = Depends(verify_service_auth)
):
    return await mech_service.handle_mechanic_assist(ctx, request)

@api_router.post("/video-search", response_model=VideoSearchResponse)
async def video_search(
    request: VideoSearchRequest, ctx: ServiceContext = Depends(verify_service_auth)
):
    return await video_service.handle_video_search(ctx, request)

@api_router.post("/extract", response_model=DocumentExtractionResponse)
async def extract_document(
    request: DocumentExtractionRequest, ctx: ServiceContext = Depends(verify_service_auth)
):
    return await extract_service.handle_extraction(ctx, request)

@api_router.post("/draft-message", response_model=CustomerMessageDraftResponse)
async def draft_message(
    request: CustomerMessageDraftRequest, ctx: ServiceContext = Depends(verify_service_auth)
):
    return await comm_service.handle_draft_message(ctx, request)

@api_router.post("/generate-quote-items", response_model=QuoteProposalResponse)
async def generate_quote_items(
    request: QuoteGenerationRequest, ctx: ServiceContext = Depends(verify_service_auth)
):
    return await quote_service.handle_quote_generation(ctx, request)

@api_router.post("/summarize-work-order", response_model=WorkOrderSummaryResponse)
async def summarize_work_order(
    request: WorkOrderSummaryRequest, ctx: ServiceContext = Depends(verify_service_auth)
):
    return await summary_service.handle_summary(ctx, request)

@api_router.post("/analytics/insights", response_model=AnalyticsInsightsResponse)
async def analytics_insights(
    request: AnalyticsInsightsRequest, ctx: ServiceContext = Depends(verify_service_auth)
):
    return await analytics_service.handle_insights(ctx, request)
