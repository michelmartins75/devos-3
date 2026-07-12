import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from devos_api import __version__
from devos_api.config import get_settings
from devos_api.logging import configure_logging, tenant_id_ctx
from devos_api.middleware.tenant import TenantContextMiddleware

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(title=settings.app_name, version=__version__)
    origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(TenantContextMiddleware)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "environment": settings.environment}

    @app.get("/api/v1/status")
    def status() -> dict[str, str | None]:
        return {
            "status": "ok",
            "environment": settings.environment,
            "version": __version__,
            "tenant_id": tenant_id_ctx.get(),
        }

    return app


app = create_app()
