from fastapi import FastAPI
from .settings import settings

# Routers
from .routers import shipments, parcels, addresses, tracking, analytics

#print(f"[BOOT] Using APP_NAME={settings.APP_NAME!r}, APP_ENV={settings.APP_ENV!r}, DEBUG={settings.APP_DEBUG!r}")

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