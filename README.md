# Logistics Data-Driven API

FastAPI + SQLAlchemy 2.0 + Alembic + PostGIS. Data-driven logistics primitives (shipments, parcels, depots, routes, stops) and geo endpoints.

## 🚀 Quickstart (Docker)

```bash
cp .env.example .env  # container uses POSTGRES_HOST=db
docker compose up -d --build
docker compose exec api alembic upgrade head
docker compose exec api python -m scripts.seed
```

### Health Check

```
curl http://localhost:8000/health
```

#### Sample Request

- Create  two addresses:

```bash
curl -X POST http://localhost:8000/api/addresses \
  -H 'content-type: application/json' \
  -d '{"name":"Sender Co","line1":"Street 1","city":"Amsterdam","zip_code":"1011AB","country_code":"NL","lat":52.37,"lon":4.90}'

curl -X POST http://localhost:8000/api/addresses \
  -H 'content-type: application/json' \
  -d '{"name":"Receiver Co","line1":"Street 2","city":"Rotterdam","zip_code":"3011AB","country_code":"NL","lat":51.92,"lon":4.48}'
```

- KPIs:

```bash
curl http://localhost:8000/api/analytics/kpis
```

- Geo:

```bash
curl "http://localhost:8000/api/geo/distance?from_lat=52.37&from_lon=4.90&to_lat=51.92&to_lon=4.48"
curl "http://localhost:8000/api/geo/nearest-depot?lat=52.37&lon=4.90"
curl http://localhost:8000/api/geo/route-length/1
```

### Migrations

- Generate: ``docker compose exec api alembic revision --autogenerate -m "..."``

- Upgrade: ``docker compose exec api alembic upgrade head``

Running Alembic on host? Use ``POSTGRES_HOST=localhost``. Container uses ``POSTGRES_HOST=db``.

## Dev tips

``scripts/seed.py`` provides demo data.

Pydantic v2: response models use ``ConfigDict(from_attributes=True)``.

PostGIS geography(Point,4326) is used for distances. ``geom`` is auto-populated on address create if ``lat/lon`` provided.
