from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from prometheus_fastapi_instrumentator import Instrumentator

from .logging_setup import configure_logging

# Routers
from .routers import addresses, analytics, geo, parcels, shipments, tracking
from .settings import settings

# Keep using settings for title; read optional version/description safely
app = FastAPI(
    title=settings.APP_NAME,
    version=getattr(settings, "APP_VERSION", "1.0.0"),
    description=getattr(
        settings,
        "APP_DESCRIPTION",
        "REST API for data-driven logistics: shipments, parcels, routes, geo & analytics.",
    ),
)

configure_logging()  # JSON logs
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


def custom_openapi():
    """Customize OpenAPI with settings-aware metadata."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    app.openapi_schema = schema
    return app.openapi_schema


# Replace the default OpenAPI generator
app.openapi = custom_openapi  # type: ignore


@app.get("/swagger", include_in_schema=False)
def custom_swagger():
    """Vanity Swagger UI endpoint (in addition to /docs)."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} – Swagger",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


# Include routers
app.include_router(addresses.router)
app.include_router(shipments.router)
app.include_router(parcels.router)
app.include_router(tracking.router)
app.include_router(analytics.router)
app.include_router(geo.router)
