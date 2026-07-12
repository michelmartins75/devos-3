import logging
from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from devos_api.logging import tenant_id_ctx

logger = logging.getLogger(__name__)

# TODO(ADR-003): replace provisional internal header with authenticated tenant resolution.
TENANT_HEADER = "X-Tenant-ID"


class TenantContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        raw_tenant_id = request.headers.get(TENANT_HEADER)
        token = tenant_id_ctx.set(raw_tenant_id)
        try:
            if raw_tenant_id is not None:
                try:
                    UUID(raw_tenant_id)
                except ValueError:
                    logger.warning(
                        "invalid tenant header rejected", extra={"tenant_id": raw_tenant_id}
                    )
                    return Response(status_code=400, content='{"detail":"invalid tenant id"}')
            response = await call_next(request)
            if raw_tenant_id is not None:
                response.headers[TENANT_HEADER] = raw_tenant_id
            return response
        finally:
            tenant_id_ctx.reset(token)
