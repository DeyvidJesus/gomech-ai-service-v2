from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.router import api_router, health_router
from app.core.config import settings
from app.core.observability import AI_GUARDRAIL_VIOLATIONS, logger, setup_logging
from app.domain.exceptions import (
    AiServiceError,
    GuardrailViolationError,
    RateLimitError,
    TimeoutError,
)
from app.infrastructure.isolation_guard import verify_zero_database_isolation


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.LOG_LEVEL)
    logger.info("Initializing GoMech AI Service", extra={"service": settings.AI_SERVICE_NAME})

    verify_zero_database_isolation()
    logger.info("Architectural check passed: Zero database drivers detected.")

    yield
    logger.info("Shutting down GoMech AI Service")


app = FastAPI(
    title="GoMech AI Service",
    description="Stateless, independently deployable AI service providing automotive intelligence.",
    version=settings.AI_SERVICE_VERSION,
    lifespan=lifespan,
)


@app.exception_handler(GuardrailViolationError)
async def guardrail_violation_handler(request: Request, exc: GuardrailViolationError):
    AI_GUARDRAIL_VIOLATIONS.labels(capability="GLOBAL", rule=exc.rule).inc()
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "type": "https://gomech.com/errors/guardrail-violation",
            "title": "Guardrail Violation",
            "status": 422,
            "detail": exc.message,
            "rule": exc.rule,
            "error_code": exc.error_code,
        },
    )


@app.exception_handler(RateLimitError)
async def rate_limit_handler(request: Request, exc: RateLimitError):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        headers={"Retry-After": str(exc.retry_after)},
        content={
            "type": "https://gomech.com/errors/rate-limit",
            "title": "Rate Limit Exceeded",
            "status": 429,
            "detail": exc.message,
            "error_code": exc.error_code,
        },
    )


@app.exception_handler(TimeoutError)
async def timeout_handler(request: Request, exc: TimeoutError):
    return JSONResponse(
        status_code=status.HTTP_504_GATEWAY_TIMEOUT,
        content={
            "type": "https://gomech.com/errors/timeout",
            "title": "Gateway Timeout",
            "status": 504,
            "detail": exc.message,
            "error_code": exc.error_code,
        },
    )


@app.exception_handler(AiServiceError)
async def ai_service_error_handler(request: Request, exc: AiServiceError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "https://gomech.com/errors/ai-service",
            "title": "AI Service Error",
            "status": exc.status_code,
            "detail": exc.message,
            "error_code": exc.error_code,
        },
    )


app.include_router(health_router)
app.include_router(api_router)
