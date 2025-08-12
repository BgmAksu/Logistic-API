from fastapi import FastAPI

app = FastAPI(title="Logistics Data-Driven API")

@app.get("/health")
def health():
    return {"status": "ok"}