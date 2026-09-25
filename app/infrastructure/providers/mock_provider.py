from decimal import Decimal

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
    ExtractedInvoiceItem,
    GroundingCitation,
    MaintenanceRecommendationRequest,
    MaintenanceRecommendationResponse,
    MaintenanceScheduleItem,
    MechanicAssistRequest,
    MechanicAssistResponse,
    PartsRecommendationRequest,
    PartsRecommendationResponse,
    ProposedQuoteItem,
    QuoteGenerationRequest,
    QuoteProposalResponse,
    RecommendedPartItem,
    TorqueSpecification,
    UsageMetadata,
    VideoSearchRequest,
    VideoSearchResponse,
    VideoSearchResultItem,
    WorkOrderSummaryRequest,
    WorkOrderSummaryResponse,
)
from app.infrastructure.providers.base import AiProvider


class MockAiProvider(AiProvider):
    """Deterministic, domain-rich automotive AI provider for isolated local testing & fallback."""

    @property
    def provider_name(self) -> str:
        return "mock-automotive-intelligence"

    async def chat(self, request: ChatRequest) -> ChatResponse:
        last_msg = request.messages[-1].content if request.messages else ""
        vehicle = request.context_vehicle or "veículo especificado"

        reply = (
            f"Com base na documentação técnica para o {vehicle}, "
            f"analisei sua dúvida sobre '{last_msg}'. "
            "Recomendo verificar as especificações do manual de serviço e calibragem correta dos atuadores."
        )

        citations = [
            GroundingCitation(
                source_title="Manual de Serviço Automotivo GoMech",
                document_reference="GOM-TECH-2026-V1",
                snippet=f"Diretrizes técnicas de inspeção aplicadas para {vehicle}.",
                relevance_score=0.94,
            )
        ]

        return ChatResponse(
            reply=reply,
            citations=citations,
            usage=UsageMetadata(
                model_used="mock-turbo",
                prompt_tokens=80,
                completion_tokens=95,
                total_tokens=175,
                latency_ms=45,
            ),
        )

    async def diagnose(self, request: DiagnosticRequest) -> DiagnosticResponse:
        fault_codes = request.fault_codes or []
        symptoms = request.symptoms_description.lower()

        if "p0300" in [c.lower() for c in fault_codes] or "falhando" in symptoms or "engasgando" in symptoms:
            summary = "Identificado padrão de falha de ignição/injeção intermitente no ciclo de combustão."
            causes = [
                "Desgaste excessivo dos eletrodos das velas de ignição",
                "Fuga de corrente nos cabos de vela ou bobinas individuais",
                "Bicos injetores carbonizados ou com vazão desequalizada",
            ]
            steps = [
                "1. Teste de centelhamento e resistência primária/secundária das bobinas.",
                "2. Inspeção visual e medição de gap das velas de ignição.",
                "3. Medição de pressão e vazão da linha de combustível.",
            ]
            checklist = ["Velas de Ignição", "Bobinas de Ignição", "Limpeza de Bicos Injetores"]
            warnings = ["Evitar acelerações bruscas sob carga para não danificar o catalisador."]
        elif "freio" in symptoms or "barulho" in symptoms or "chiado" in symptoms:
            summary = "Desgaste mecânico avançado no conjunto de fricção do sistema de frenagem."
            causes = [
                "Pastilhas de freio no limite de espessura de segurança",
                "Discos de freio com ranhuras ou empenamento",
                "Fluido de freio com ponto de ebulição degradado por umidade",
            ]
            steps = [
                "1. Medir espessura das pastilhas e espessura residual dos discos com micrômetro.",
                "2. Testar teor de umidade no reservatório do fluido de freio DOT 4.",
            ]
            checklist = ["Pastilhas de Freio Dianteiras", "Discos de Freio Dianteiros", "Fluido DOT 4"]
            warnings = ["Atenção: Espessura residual de disco inferior à tolerância exige substituição imediata."]
        else:
            summary = "Padrão de anomalia veicular geral inferido a partir dos parâmetros relatados."
            causes = [
                "Desgaste em buchas e terminais da suspensão dianteira",
                "Filtros de ar ou combustível saturados",
            ]
            steps = [
                "1. Inspeção mecânica em elevador com teste de folgas.",
                "2. Leitura de parâmetros dinâmicos via scanner OBD-II.",
            ]
            checklist = ["Checklist de Suspensão", "Diagnóstico Eletrônico Scanner"]
            warnings = []

        return DiagnosticResponse(
            diagnosis_summary=summary,
            probable_causes=causes,
            recommended_inspection_steps=steps,
            confidence_score=0.92,
            proposed_action="PROPOSE_QUOTE_ITEMS",
            proposed_checklist=checklist,
            safety_warnings=warnings,
            usage=UsageMetadata(
                model_used="mock-reasoning-pro",
                prompt_tokens=160,
                completion_tokens=210,
                total_tokens=370,
                latency_ms=75,
            ),
        )

    async def recommend_parts(self, request: PartsRecommendationRequest) -> PartsRecommendationResponse:
        make = request.vehicle_make
        model = request.vehicle_model
        km = request.current_odometer_km

        parts = [
            RecommendedPartItem(
                part_name="Kit de Correia Dentada e Tensor",
                part_number="CT-909-K1",
                category="MOTOR",
                quantity=Decimal("1"),
                urgency="CRITICAL" if km >= 60000 else "PREVENTIVE",
                rationale=f"Recomendação de troca preventiva pelo plano de manutenção aos {km} km.",
                estimated_cost=Decimal("380.00"),
                grounding_reference=f"Manual de Manutenção Preventiva {make} {model}",
            ),
            RecommendedPartItem(
                part_name="Filtro de Óleo e Óleo 5W30 Sintético",
                part_number="LUB-5W30-4L",
                category="LUBRIFICAÇÃO",
                quantity=Decimal("4"),
                urgency="RECOMMENDED",
                rationale="Substituição regular a cada 10.000 km.",
                estimated_cost=Decimal("220.00"),
                grounding_reference="Especificação API SP / ACEA A5/B5",
            ),
        ]

        citations = [
            GroundingCitation(
                source_title=f"Manual Técnico do Fabricante - {make} {model}",
                document_reference=f"MAN-{make.upper()}-{model.upper()}-2026",
                snippet="Plano de revisões programadas: troca do kit de distribuição e lubrificantes a cada 50.000~60.000 km.",
                relevance_score=0.96,
            )
        ]

        return PartsRecommendationResponse(
            vehicle_summary=f"{make} {model} {request.vehicle_year} ({km:,} km)",
            recommended_parts=parts,
            preventive_actions=[
                "Verificar estado da bomba d'água ao substituir o kit de correia.",
                "Checar nível e estanqueidade do líquido de arrefecimento.",
            ],
            confidence_score=0.94,
            citations=citations,
            safety_disclaimer="Recomendações técnicas geradas por IA baseadas no plano de manutenção. Confirme a aplicação física antes da instalação.",
            usage=UsageMetadata(
                model_used="mock-reasoning-pro",
                prompt_tokens=190,
                completion_tokens=240,
                total_tokens=430,
                latency_ms=80,
            ),
        )

    async def recommend_maintenance(self, request: MaintenanceRecommendationRequest) -> MaintenanceRecommendationResponse:
        km = request.current_odometer_km
        next_due = ((km // 10000) + 1) * 10000

        items = [
            MaintenanceScheduleItem(
                interval_km=next_due,
                description=f"Revisão Periódica dos {next_due:,} km",
                mandatory_items=["Óleo do Motor", "Filtro de Óleo", "Filtro de Combustível", "Filtro de Ar"],
                inspection_items=["Pastilhas de Freio", "Fluido de Freio", "Correias Auxiliares", "Suspensão"],
            )
        ]

        return MaintenanceRecommendationResponse(
            next_due_service_km=next_due,
            schedule_items=items,
            recommendations_summary=f"Plano de manutenção preventiva alinhado para {request.vehicle_make} {request.vehicle_model} aos {next_due:,} km.",
            confidence_score=0.95,
            usage=UsageMetadata(
                model_used="mock-turbo",
                prompt_tokens=90,
                completion_tokens=110,
                total_tokens=200,
                latency_ms=50,
            ),
        )

    async def assist_mechanic(self, request: MechanicAssistRequest) -> MechanicAssistResponse:
        comp = request.target_component.lower()

        if "cabeçote" in comp or "cilindro" in comp:
            title = f"Procedimento de Aperto do Cabeçote - {request.vehicle_make} {request.vehicle_model}"
            steps = [
                "1. Limpar rigorosamente a face do bloco e do cabeçote com desengraxante não corrosivo.",
                "2. Posicionar a junta metálica nova atentando para a marcação TOP / TOP UP.",
                "3. Lubrificar levemente a rosca e a face de apoio dos parafusos novos.",
                "4. Aplicar o torque na sequência em espiral a partir do centro para as extremidades.",
            ]
            torques = [
                TorqueSpecification(
                    fastener_location="Parafusos M10 do Cabeçote",
                    tightening_spec="30 Nm + 90° + 90°",
                    stage_sequence=[
                        "Fase 1: 30 Nm em sequência espiral",
                        "Fase 2: Aperto angular de 90°",
                        "Fase 3: Aperto angular final de 90°",
                    ],
                )
            ]
            tools = ["Torquímetro 10-100 Nm", "Goniômetro angular", "Soquete Ribe / Torx E14"]
        else:
            title = f"Procedimento Técnico para {request.target_component}"
            steps = [
                "1. Elevar o veículo e calçar com cavaletes de segurança.",
                "2. Desconectar o terminal negativo da bateria antes da intervenção.",
                "3. Desmontar o componente seguindo a ordem de descompressão.",
                "4. Montar com novos fixadores aplicando o torque tabelado.",
            ]
            torques = [
                TorqueSpecification(
                    fastener_location="Parafusos de Fixação",
                    tightening_spec="45 Nm",
                    stage_sequence=["Aperto único de 45 Nm"],
                )
            ]
            tools = ["Jogo de chaves combinadas", "Torquímetro de precisão"]

        citations = [
            GroundingCitation(
                source_title="Manual de Oficina e Especificações de Torque",
                document_reference="SPEC-TORQUE-2026",
                snippet=f"Tabela de torques e ângulos para {request.vehicle_make} {request.vehicle_model}.",
                relevance_score=0.98,
            )
        ]

        return MechanicAssistResponse(
            procedure_title=title,
            step_by_step_guide=steps,
            torque_specifications=torques,
            special_tools_required=tools,
            safety_precautions=[
                "Utilizar sempre parafusos novos em juntas com aperto angular (torque de rendimento plástico).",
                "Aguardar o resfriamento completo do motor antes de desapertar o cabeçote.",
            ],
            confidence_score=0.96,
            citations=citations,
            usage=UsageMetadata(
                model_used="mock-reasoning-pro",
                prompt_tokens=180,
                completion_tokens=250,
                total_tokens=430,
                latency_ms=85,
            ),
        )

    async def search_video(self, request: VideoSearchRequest) -> VideoSearchResponse:
        results = [
            VideoSearchResultItem(
                title=f"Como trocar {request.procedure_topic} no {request.vehicle_info} passo a passo",
                author_or_source="Doutor-IE / Mecânica Ao Vivo",
                url="https://youtube.com/watch?v=example-video-1",
                thumbnail_url="https://img.youtube.com/vi/example-video-1/hqdefault.jpg",
                duration_seconds=740,
                relevance_summary=f"Guia prático demonstrando o procedimento completo para {request.procedure_topic} com dicas de ferramentas e torques.",
            ),
            VideoSearchResultItem(
                title=f"Diagnóstico de defeitos comuns no {request.vehicle_info}",
                author_or_source="Oficina Conectada",
                url="https://youtube.com/watch?v=example-video-2",
                thumbnail_url="https://img.youtube.com/vi/example-video-2/hqdefault.jpg",
                duration_seconds=520,
                relevance_summary="Análise de sintomas e interpretação de códigos de scanner com osciloscópio.",
            ),
        ]

        return VideoSearchResponse(
            topic=request.procedure_topic,
            results=results,
            usage=UsageMetadata(
                model_used="mock-turbo",
                prompt_tokens=60,
                completion_tokens=140,
                total_tokens=200,
                latency_ms=40,
            ),
        )

    async def extract_document(self, request: DocumentExtractionRequest) -> DocumentExtractionResponse:
        items = [
            ExtractedInvoiceItem(
                item_type="PART",
                code_or_sku="AMOR-DIANT-01",
                description="Amortecedor Dianteiro Pressurizado",
                quantity=Decimal("2"),
                unit_price=Decimal("320.00"),
                total_price=Decimal("640.00"),
            ),
            ExtractedInvoiceItem(
                item_type="PART",
                code_or_sku="KIT-BATENTE-01",
                description="Kit Batente e Coifa do Amortecedor",
                quantity=Decimal("2"),
                unit_price=Decimal("65.00"),
                total_price=Decimal("130.00"),
            ),
        ]

        return DocumentExtractionResponse(
            document_type=request.document_type,
            supplier_name="Distribuidora de Autopeças Brasil LTDA",
            document_number="NF-e 001.458.982",
            date="2026-08-25",
            extracted_items=items,
            total_amount=Decimal("770.00"),
            extraction_confidence=0.98,
            usage=UsageMetadata(
                model_used="mock-vision-pro",
                prompt_tokens=150,
                completion_tokens=180,
                total_tokens=330,
                latency_ms=90,
            ),
        )

    async def draft_message(self, request: CustomerMessageDraftRequest) -> CustomerMessageDraftResponse:
        customer = request.customer_name or "Cliente"
        plate = f" ({request.vehicle_plate})" if request.vehicle_plate else ""
        subject = f"GoMech: Atualização do seu veículo{plate}"

        if request.topic == "QUOTE_READY":
            body = (
                f"Olá, {customer}! O orçamento técnico para a revisão do seu veículo{plate} já está concluído. "
                "Disponibilizamos todos os itens detalhados com valores de peças e mão de obra em nosso link seguro. "
                "Ficamos à disposição para tirar qualquer dúvida!"
            )
        elif request.topic == "SERVICE_COMPLETED":
            body = (
                f"Olá, {customer}! Informamos que os serviços no seu veículo{plate} foram concluídos com sucesso. "
                "Seu carro foi inspecionado, testado e já está pronto para retirada em nossa oficina. Aguardamos sua visita!"
            )
        else:
            body = (
                f"Olá, {customer}! Temos uma atualização sobre o andamento dos serviços no seu veículo{plate}: "
                f"{request.key_details or 'Aguardamos seu contato para alinharmos os próximos passos.'}"
            )

        return CustomerMessageDraftResponse(
            channel="WHATSAPP",
            subject=subject,
            body_message=body,
            usage=UsageMetadata(
                model_used="mock-turbo",
                prompt_tokens=70,
                completion_tokens=90,
                total_tokens=160,
                latency_ms=35,
            ),
        )

    async def generate_quote(self, request: QuoteGenerationRequest) -> QuoteProposalResponse:
        items = [
            ProposedQuoteItem(
                type="SERVICE",
                description="Mão de Obra: Revisão e Calibração de Ignição / Injeção",
                part_number="MO-REV-01",
                quantity=Decimal("1"),
                estimated_price=Decimal("180.00"),
                rationale="Tempo padrão de bancada e diagnóstico: 1.5 horas",
            ),
            ProposedQuoteItem(
                type="PART",
                description="Jogo de Velas de Ignição Iridium",
                part_number="NGK-BKR6EIX",
                quantity=Decimal("4"),
                estimated_price=Decimal("240.00"),
                rationale="Substituição preventiva recomendada pelo diagnóstico",
            ),
            ProposedQuoteItem(
                type="PART",
                description="Filtro de Combustível Injeção",
                part_number="FIL-FC-120",
                quantity=Decimal("1"),
                estimated_price=Decimal("45.00"),
                rationale="Troca preventiva do elemento filtrante",
            ),
        ]

        labor = Decimal("180.00")
        parts = Decimal("285.00")
        total = labor + parts

        return QuoteProposalResponse(
            summary=f"Orçamento preliminar gerado para {request.vehicle_info} com base no laudo técnico.",
            proposed_items=items,
            estimated_total_labor=labor,
            estimated_total_parts=parts,
            total_estimate=total,
            usage=UsageMetadata(
                model_used="mock-reasoning-pro",
                prompt_tokens=180,
                completion_tokens=220,
                total_tokens=400,
                latency_ms=75,
            ),
        )

    async def summarize_work_order(self, request: WorkOrderSummaryRequest) -> WorkOrderSummaryResponse:
        order_no = request.order_number or "OS"
        tech = (
            f"{order_no}: Realizada inspeção de entrada para as queixas '{request.customer_reported_issues}'. "
            f"Executados: {', '.join(request.services_performed) if request.services_performed else 'serviços de revisão'}. "
            f"Peças substituídas: {', '.join(request.parts_replaced) if request.parts_replaced else 'peças conformes'}. "
            f"Notas do mecânico: {request.mechanic_notes or 'Veículo testado e aprovado em dinamômetro e rodagem.'}"
        )

        exec_summary = (
            f"Olá! Seu veículo ({request.vehicle_summary}) passou por uma revisão minuciosa em nossa oficina. "
            "Todos os serviços foram executados seguindo as normas dos fabricantes e os testes de qualidade foram 100% aprovados."
        )

        return WorkOrderSummaryResponse(
            technical_summary=tech,
            executive_customer_summary=exec_summary,
            preventive_recommendations=[
                "Retorno preventivo em 10.000 km ou 6 meses para alinhamento e balanceamento.",
                "Checagem periódica do nível do óleo e pressão dos pneus a cada 15 dias.",
            ],
            warranty_terms="Garantia legal de 90 dias sobre serviços e peças genuínas aplicadas.",
            usage=UsageMetadata(
                model_used="mock-turbo",
                prompt_tokens=150,
                completion_tokens=180,
                total_tokens=330,
                latency_ms=65,
            ),
        )

    async def generate_insights(self, request: AnalyticsInsightsRequest) -> AnalyticsInsightsResponse:
        kpi_count = len(request.kpis)
        return AnalyticsInsightsResponse(
            executive_overview=(
                f"Análise executiva referente ao período '{request.period_description}'. "
                f"Processados {kpi_count} indicadores de performance operacional e financeira."
            ),
            key_highlights=[
                "Aumento de 12% na taxa de conversão de orçamentos em relação ao ciclo anterior.",
                "Tempo médio de permanência em box (lead time) mantido dentro da meta operacional (< 4.5h).",
            ],
            operational_bottlenecks=[
                "Gargalo identificado no fornecimento de peças de suspensão para marcas importadas (lead time de entrega > 48h).",
            ],
            actionable_recommendations=[
                "Padronizar kits de revisão rápida em estoque para os 3 modelos mais atendidos na oficina.",
                "Implementar pré-agendamento de peças com 24h de antecedência aos agendamentos confirmados.",
            ],
            usage=UsageMetadata(
                model_used="mock-reasoning-pro",
                prompt_tokens=140,
                completion_tokens=200,
                total_tokens=340,
                latency_ms=70,
            ),
        )
