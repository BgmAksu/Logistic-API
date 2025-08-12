# Logistics Data-Driven API (FastAPI)


## Config
- Copy file:`.env.example` to `.env` and adjust to your local.

## Docker (dev)
```bash
# copy env
cp .env.example .env

# build & start
docker compose up --build -d

# API: http://localhost:8000/docs