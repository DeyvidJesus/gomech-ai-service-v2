from uuid import UUID

from fastapi import Header, HTTPException, status
from pydantic import BaseModel

from app.core.config import settings


class ServiceContext(BaseModel):
    tenant_id: UUID
    user_id: UUID | None = None
    unit_id: UUID | None = None
    correlation_id: str | None = None


async def verify_service_auth(
    x_go_mech_service_auth: str | None = Header(default=None, alias="X-GoMech-Service-Auth"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_unit_id: str | None = Header(default=None, alias="X-Unit-Id"),
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-Id"),
) -> ServiceContext:
    """
    Enforces service-to-service authentication and validates required tenant context.
    The AI service is an internal capability reachable only through the Monolith Gateway.
    """
    # 1. Validate Shared Service Secret
    provided_secret = x_go_mech_service_auth
    if not provided_secret and authorization and authorization.startswith("Bearer "):
        provided_secret = authorization.split(" ", 1)[1]

    if not provided_secret or provided_secret != settings.SERVICE_AUTH_SECRET:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing service authentication token.",
        )

    # 2. Validate Tenant Context
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad Request: X-Tenant-Id header is required.",
        )

    try:
        tenant_uuid = UUID(x_tenant_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bad Request: X-Tenant-Id must be a valid UUID.",
        )

    user_uuid: UUID | None = None
    if x_user_id:
        try:
            user_uuid = UUID(x_user_id)
        except ValueError:
            pass

    unit_uuid: UUID | None = None
    if x_unit_id:
        try:
            unit_uuid = UUID(x_unit_id)
        except ValueError:
            pass

    return ServiceContext(
        tenant_id=tenant_uuid,
        user_id=user_uuid,
        unit_id=unit_uuid,
        correlation_id=x_correlation_id,
    )
