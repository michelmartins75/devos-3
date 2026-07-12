import logging

from fastapi import FastAPI

from devos_api.config import get_settings
from devos_api.logging import configure_logging
from devos_api.middleware.tenant import TenantContextMiddleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(TenantContextMiddleware)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    return app


app = create_app()
