import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from .errors import AppError, ErrorCode
from .limits import register_rate_limit
from .logging_setup import configure_logging

# Routers
from .routers import addresses, analytics, geo, geo_optimize, parcels, shipments, tracking
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


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """Return RFC7807-like problem+json for domain errors."""
    problem = {
        "type": f"https://example.com/problems/{exc.code}",
        "title": exc.title,
        "status": exc.status,
        "detail": exc.detail,
        "instance": str(request.url),
        "code": str(exc.code),
    }
    if exc.extra:
        problem["extra"] = exc.extra
    return JSONResponse(status_code=exc.status, content=problem)


# Robust fallback: never drop connection on unexpected errors
@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logging.exception("unhandled exception")
    problem = {
        "type": f"https://example.com/problems/{ErrorCode.INTERNAL}",
        "title": "Internal server error",
        "status": 500,
        "detail": "An unexpected error occurred.",
        "instance": str(request.url),
        "code": str(ErrorCode.INTERNAL),
    }
    return JSONResponse(status_code=500, content=problem)


configure_logging()  # JSON logs
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# CORS (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiter registration (no circular import)
register_rate_limit(app)


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
app.include_router(geo_optimize.router)
