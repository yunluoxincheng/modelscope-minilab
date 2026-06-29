"""FastAPI application factory and entrypoint."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from . import __service_name__, __version__
from .api import auth as auth_api
from .api import health as health_api
from .api import models_api as models_api
from .api import predictions as predictions_api
from .core.errors import install_error_handlers, new_request_id
from .core.logging import configure_logging
from .core.settings import get_settings
from .db.bootstrap import create_all
from .db.seed import seed_models

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging("DEBUG" if settings.debug else "INFO")
    log.info("starting %s v%s env=%s", __service_name__, __version__, settings.env)
    create_all()
    seed_models()
    yield
    log.info("shutdown %s", __service_name__)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=__service_name__,
        version=__version__,
        description="智模工坊 / ModelScope MiniLab 后端推理服务",
        lifespan=lifespan,
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    if settings.cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.middleware("http")
    async def _attach_request_id(request: Request, call_next):
        response = await call_next(request)
        rid = request.headers.get("x-request-id") or new_request_id()
        response.headers["X-Request-Id"] = rid
        return response

    install_error_handlers(app)

    api_prefix = settings.api_prefix
    app.include_router(health_api.router, prefix=api_prefix)
    app.include_router(auth_api.router, prefix=api_prefix)
    app.include_router(models_api.router, prefix=api_prefix)
    app.include_router(predictions_api.router, prefix=api_prefix)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
