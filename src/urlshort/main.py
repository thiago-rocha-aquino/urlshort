from __future__ import annotations

from fastapi import FastAPI

from urlshort.infrastructure.config import get_settings
from urlshort.infrastructure.logging import configure_logging
from urlshort.presentation.api.analytics import router as analytics_router
from urlshort.presentation.api.auth import router as auth_router
from urlshort.presentation.api.health import router as health_router
from urlshort.presentation.api.redirect import router as redirect_router
from urlshort.presentation.api.urls import router as urls_router
from urlshort.presentation.exception_handlers import register_exception_handlers
from urlshort.presentation.middleware.request_id import RequestIdMiddleware


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(debug=settings.app_debug)

    app = FastAPI(
        title="api_url_shortener",
        description=(
            "Encurtador de URLs com analytics granulares, cache Redis "
            "e detecao de geolocalizacao via MaxMind."
        ),
        version="0.1.0",
        debug=settings.app_debug,
    )
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(urls_router)
    app.include_router(analytics_router)
    # redirect deve ser o ultimo (catch-all "/{slug}")
    app.include_router(redirect_router)

    return app


app = create_app()
