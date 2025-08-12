from fastapi import FastAPI
from .settings import settings

#print(f"[BOOT] Using APP_NAME={settings.APP_NAME!r}, APP_ENV={settings.APP_ENV!r}, DEBUG={settings.APP_DEBUG!r}")

app = FastAPI(title=settings.APP_NAME)

@app.get("/health")
def health():
    return {"status": "ok"}