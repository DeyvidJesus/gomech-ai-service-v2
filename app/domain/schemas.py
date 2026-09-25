from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

class UsageMetadata(BaseModel):
    model_used: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0

class GroundingCitation(BaseModel):
    source_title: str
    document_reference: str
    snippet: str
    relevance_score: float = Field(ge=0.0, le=1.0)

# Chat
class ChatMessage(BaseModel):
    role: str = Field(..., description="user, assistant, or system")
    content: str

class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)
    context_vehicle: str | None = None
    max_tokens: int = 500
    temperature: float = 0.7

class ChatResponse(BaseModel):
    reply: str
    citations: list[GroundingCitation] = Field(default_factory=list)
    usage: UsageMetadata

# Diagnostics and fault codes
class DiagnosticRequest(BaseModel):
    vehicle_id: UUID | None = None
    vehicle_make: str | None = None
    vehicle_model: str | None = None
    vehicle_year: int | None = None
    odometer_km: int | None = None
    symptoms_description: str = Field(..., min_length=5, max_length=3000)
    fault_codes: list[str] = Field(default_factory=list)
    customer_notes: str | None = None

class DiagnosticResponse(BaseModel):
    diagnosis_summary: str
    probable_causes: list[str]
    recommended_inspection_steps: list[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    proposed_action: str
    proposed_checklist: list[str]
    safety_warnings: list[str] = Field(default_factory=list)
    usage: UsageMetadata

# Parts and maintenance recommendations
class VehicleHistoryItem(BaseModel):
    date: str
    description: str
    mileage_km: int | None = None
    parts_replaced: list[str] = Field(default_factory=list)

class RecommendedPartItem(BaseModel):
    part_name: str
    part_number: str | None = None
    category: str
    quantity: Decimal = Decimal("1")
    urgency: str = "RECOMMENDED"  # CRITICAL, RECOMMENDED, PREVENTIVE
    rationale: str
    estimated_cost: Decimal | None = None
    grounding_reference: str | None = None

class PartsRecommendationRequest(BaseModel):
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    current_odometer_km: int
    reported_symptoms: str | None = None
    vehicle_history: list[VehicleHistoryItem] = Field(default_factory=list)

class PartsRecommendationResponse(BaseModel):
    vehicle_summary: str
    recommended_parts: list[RecommendedPartItem]
    preventive_actions: list[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    citations: list[GroundingCitation] = Field(default_factory=list)
    safety_disclaimer: str
    usage: UsageMetadata

class MaintenanceScheduleItem(BaseModel):
    interval_km: int
    description: str
    mandatory_items: list[str]
    inspection_items: list[str]

class MaintenanceRecommendationRequest(BaseModel):
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    current_odometer_km: int

class MaintenanceRecommendationResponse(BaseModel):
    next_due_service_km: int
    schedule_items: list[MaintenanceScheduleItem]
    recommendations_summary: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    usage: UsageMetadata

# Mechanic assistance
class MechanicAssistRequest(BaseModel):
    vehicle_make: str
    vehicle_model: str
    vehicle_year: int
    engine_or_trim: str | None = None
    target_component: str = Field(..., description="e.g. cabeçote, pastilhas dianteiras, embreagem")
    question_or_procedure: str

class TorqueSpecification(BaseModel):
    fastener_location: str
    tightening_spec: str
    stage_sequence: list[str] = Field(default_factory=list)

class MechanicAssistResponse(BaseModel):
    procedure_title: str
    step_by_step_guide: list[str]
    torque_specifications: list[TorqueSpecification] = Field(default_factory=list)
    special_tools_required: list[str] = Field(default_factory=list)
    safety_precautions: list[str]
    confidence_score: float = Field(ge=0.0, le=1.0)
    citations: list[GroundingCitation] = Field(default_factory=list)
    usage: UsageMetadata

# Technical video and procedure search
class VideoSearchResultItem(BaseModel):
    title: str
    author_or_source: str
    url: str
    thumbnail_url: str | None = None
    duration_seconds: int | None = None
    relevance_summary: str

class VideoSearchRequest(BaseModel):
    vehicle_info: str
    procedure_topic: str

class VideoSearchResponse(BaseModel):
    topic: str
    results: list[VideoSearchResultItem]
    usage: UsageMetadata

# Document and invoice extraction
class ExtractedInvoiceItem(BaseModel):
    item_type: str  # PART, SERVICE, OTHER
    code_or_sku: str | None = None
    description: str
    quantity: Decimal
    unit_price: Decimal
    total_price: Decimal

class DocumentExtractionRequest(BaseModel):
    document_type: str = "INVOICE"  # INVOICE, INSPECTION_SHEET, PARTS_CATALOG
    raw_text_content: str = Field(..., min_length=10)

class DocumentExtractionResponse(BaseModel):
    document_type: str
    supplier_name: str | None = None
    document_number: str | None = None
    date: str | None = None
    extracted_items: list[ExtractedInvoiceItem]
    total_amount: Decimal | None = None
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    usage: UsageMetadata

# Customer communication drafts
class CustomerMessageDraftRequest(BaseModel):
    customer_id: UUID | None = None
    customer_name: str
    vehicle_plate: str | None = None
    topic: str = "QUOTE_READY"  # QUOTE_READY, SERVICE_COMPLETED, ADDITIONAL_APPROVAL_NEEDED, PAYMENT_CONFIRMATION
    key_details: str | None = None
    tone: str = "CORDIAL"  # CORDIAL, TECHNICAL, FORMAL

class CustomerMessageDraftResponse(BaseModel):
    channel: str = "WHATSAPP"
    subject: str
    body_message: str
    usage: UsageMetadata

# Quote item proposals
class ProposedQuoteItem(BaseModel):
    type: str  # SERVICE, PART
    description: str
    part_number: str | None = None
    quantity: Decimal
    estimated_price: Decimal
    rationale: str

class QuoteGenerationRequest(BaseModel):
    work_order_id: UUID | None = None
    vehicle_info: str
    diagnostic_summary: str
    customer_budget_limit: Decimal | None = None

class QuoteProposalResponse(BaseModel):
    summary: str
    proposed_items: list[ProposedQuoteItem]
    estimated_total_labor: Decimal
    estimated_total_parts: Decimal
    total_estimate: Decimal
    usage: UsageMetadata

# Work order summaries
class WorkOrderSummaryRequest(BaseModel):
    work_order_id: UUID | None = None
    order_number: str | None = None
    vehicle_summary: str
    customer_reported_issues: str
    services_performed: list[str] = Field(default_factory=list)
    parts_replaced: list[str] = Field(default_factory=list)
    mechanic_notes: str | None = None

class WorkOrderSummaryResponse(BaseModel):
    technical_summary: str
    executive_customer_summary: str
    preventive_recommendations: list[str]
    warranty_terms: str
    usage: UsageMetadata

# Analytics insights
class AnalyticsInsightsRequest(BaseModel):
    period_description: str
    kpis: dict[str, Any]
    focus_area: str | None = None

class AnalyticsInsightsResponse(BaseModel):
    executive_overview: str
    key_highlights: list[str]
    operational_bottlenecks: list[str]
    actionable_recommendations: list[str]
    usage: UsageMetadata
