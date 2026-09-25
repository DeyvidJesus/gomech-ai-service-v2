from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
AUTH_HEADERS = {
    "X-GoMech-Service-Auth": "gm-ai-internal-hmac-secret",
    "X-Tenant-Id": str(uuid4()),
    "X-User-Id": str(uuid4()),
    "X-Correlation-Id": "test-corr-cap-1",
}


def test_chat_capability():
    response = client.post(
        "/api/v1/ai/chat",
        headers=AUTH_HEADERS,
        json={
            "messages": [
                {"role": "user", "content": "Qual o procedimento para sangria do freio ABS?"}
            ],
            "context_vehicle": "VW Gol 1.0 2021",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["citations"]) > 0
    assert data["citations"][0]["relevance_score"] >= 0.8
    assert data["usage"]["latency_ms"] > 0


def test_diagnostics_capability():
    response = client.post(
        "/api/v1/ai/diagnose",
        headers=AUTH_HEADERS,
        json={
            "vehicle_make": "Volkswagen",
            "vehicle_model": "Golf 1.4 TSI",
            "vehicle_year": 2018,
            "odometer_km": 72000,
            "symptoms_description": "Motor falhando em subidas com luz de injeção piscando",
            "fault_codes": ["P0300", "P0302"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "falha de ignição" in data["diagnosis_summary"].lower()
    assert len(data["probable_causes"]) > 0
    assert len(data["recommended_inspection_steps"]) > 0
    assert data["confidence_score"] >= 0.85
    assert data["proposed_action"] == "PROPOSE_QUOTE_ITEMS"
    assert len(data["proposed_checklist"]) > 0


def test_parts_recommendations_capability():
    response = client.post(
        "/api/v1/ai/recommendations/parts",
        headers=AUTH_HEADERS,
        json={
            "vehicle_make": "Toyota",
            "vehicle_model": "Corolla",
            "vehicle_year": 2020,
            "current_odometer_km": 62000,
            "reported_symptoms": "Revisão periódica recomendada",
            "vehicle_history": [
                {
                    "date": "2025-08-10",
                    "description": "Troca de óleo e filtro aos 50.000 km",
                    "mileage_km": 50000,
                    "parts_replaced": ["Filtro de Óleo", "Óleo 5W30"],
                }
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "vehicle_summary" in data
    assert len(data["recommended_parts"]) > 0
    assert data["confidence_score"] >= 0.85
    assert len(data["citations"]) > 0
    assert "safety_disclaimer" in data
    part = data["recommended_parts"][0]
    assert "part_name" in part
    assert "quantity" in part
    assert "rationale" in part


def test_maintenance_recommendations_capability():
    response = client.post(
        "/api/v1/ai/recommendations/maintenance",
        headers=AUTH_HEADERS,
        json={
            "vehicle_make": "Honda",
            "vehicle_model": "Civic",
            "vehicle_year": 2021,
            "current_odometer_km": 38500,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["next_due_service_km"] == 40000
    assert len(data["schedule_items"]) > 0
    assert len(data["schedule_items"][0]["mandatory_items"]) > 0


def test_mechanic_assistance_capability():
    response = client.post(
        "/api/v1/ai/mechanic-assist",
        headers=AUTH_HEADERS,
        json={
            "vehicle_make": "Chevrolet",
            "vehicle_model": "Onix 1.0 Turbo",
            "vehicle_year": 2022,
            "target_component": "Cabeçote do Motor",
            "question_or_procedure": "Qual a sequência e torque de aperto dos parafusos do cabeçote?",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "Cabeçote" in data["procedure_title"]
    assert len(data["step_by_step_guide"]) > 0
    assert len(data["torque_specifications"]) > 0
    assert "Nm" in data["torque_specifications"][0]["tightening_spec"]
    assert len(data["safety_precautions"]) > 0


def test_video_search_capability():
    response = client.post(
        "/api/v1/ai/video-search",
        headers=AUTH_HEADERS,
        json={
            "vehicle_info": "Fiat Strada 1.3 Firefly",
            "procedure_topic": "troca da correia dentada",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) > 0
    assert "url" in data["results"][0]
    assert "title" in data["results"][0]


def test_document_extraction_capability():
    response = client.post(
        "/api/v1/ai/extract",
        headers=AUTH_HEADERS,
        json={
            "document_type": "INVOICE",
            "raw_text_content": "DANFE NF-E 001.458.982 DISTRIBUIDORA AUTOPECAS BRASIL LTDA 2x AMORTECEDOR DIANTEIRO R$ 320,00 TOTAL R$ 640,00 2x KIT BATENTE R$ 65,00 TOTAL R$ 130,00 TOTAL NOTA R$ 770,00",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["extracted_items"]) == 2
    assert float(data["total_amount"]) == 770.0
    assert data["extraction_confidence"] >= 0.9


def test_customer_message_draft_capability():
    response = client.post(
        "/api/v1/ai/draft-message",
        headers=AUTH_HEADERS,
        json={
            "customer_name": "Carlos Eduardo",
            "vehicle_plate": "ABC1D23",
            "topic": "QUOTE_READY",
            "key_details": "Orçamento de R$ 450,00 para troca de velas e filtro",
            "tone": "CORDIAL",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "Carlos Eduardo" in data["body_message"]
    assert "orçamento" in data["body_message"].lower()


def test_quote_generation_capability():
    response = client.post(
        "/api/v1/ai/generate-quote-items",
        headers=AUTH_HEADERS,
        json={
            "vehicle_info": "Hyundai HB20 1.0 2020",
            "diagnostic_summary": "Falha de ignição por velas carbonizadas",
            "customer_budget_limit": 500.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["proposed_items"]) > 0
    assert float(data["total_estimate"]) > 0
    assert float(data["estimated_total_labor"]) > 0
    assert float(data["estimated_total_parts"]) > 0


def test_work_order_summary_capability():
    response = client.post(
        "/api/v1/ai/summarize-work-order",
        headers=AUTH_HEADERS,
        json={
            "order_number": "OS-2026-99",
            "vehicle_summary": "Ford Ka 1.0 2019",
            "customer_reported_issues": "Barulho de rangido na suspensão",
            "services_performed": ["Substituição dos amortecedores dianteiros"],
            "parts_replaced": ["Amortecedores Monroe", "Kits Batentes"],
            "mechanic_notes": "Veículo alinhado e balanceado após a troca.",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "OS-2026-99" in data["technical_summary"]
    assert "Olá!" in data["executive_customer_summary"]
    assert len(data["preventive_recommendations"]) > 0


def test_analytics_insights_capability():
    response = client.post(
        "/api/v1/ai/analytics/insights",
        headers=AUTH_HEADERS,
        json={
            "period_description": "Agosto de 2026",
            "kpis": {
                "total_work_orders": 142,
                "average_ticket": 850.0,
                "quote_conversion_rate": 0.78,
                "parts_margin_percentage": 34.5,
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "Agosto de 2026" in data["executive_overview"]
    assert len(data["key_highlights"]) > 0
    assert len(data["actionable_recommendations"]) > 0
