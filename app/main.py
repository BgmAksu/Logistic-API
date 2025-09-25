from fastapi import FastAPI

# Routers
from .routers import addresses, analytics, geo, parcels, shipments, tracking
from .settings import settings

app = FastAPI(title=settings.APP_NAME)


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
