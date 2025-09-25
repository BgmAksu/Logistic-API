# Geospatial endpoints using PostGIS geography functions.

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_db

router = APIRouter(prefix="/api/geo", tags=["geo"])


@router.get("/nearest-depot")
def nearest_depot(
    lat: float = Query(..., description="WGS84 latitude"),
    lon: float = Query(..., description="WGS84 longitude"),
    db: Session = Depends(get_db),
):
    # Build point in WGS84
    pt = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)

    # Join depots to their address geometries and compute distance in meters
    stmt = (
        select(models.Depot, func.ST_Distance(models.Address.geom, pt).label("distance_m"))
        .join(models.Address, models.Depot.address_id == models.Address.id)
        .where(models.Address.geom.is_not(None))
        .order_by("distance_m")
        .limit(1)
    )
    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(404, "No depot with geometry found")
    depot, dist = row
    return {"depot": {"id": depot.id, "name": depot.name}, "distance_m": float(dist)}


@router.get("/distance")
def distance(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
    db: Session = Depends(get_db),
):
    a = func.ST_SetSRID(func.ST_MakePoint(from_lon, from_lat), 4326)
    b = func.ST_SetSRID(func.ST_MakePoint(to_lon, to_lat), 4326)
    d = db.scalar(select(func.ST_Distance(a, b)))
    return {"meters": float(d)}


@router.get("/route-length/{route_id}")
def route_length(route_id: int, db: Session = Depends(get_db)):
    # Compute pairwise distances between consecutive stops, then sum in the outer query.
    stmt = text(
        """
        WITH ordered AS (
            SELECT s.sequence, a.geom
            FROM stops s
            JOIN addresses a ON a.id = s.address_id
            WHERE s.route_id = :route_id
              AND a.geom IS NOT NULL
            ORDER BY s.sequence
        ),
        pairs AS (
            SELECT sequence,
                   geom,
                   LAG(geom) OVER (ORDER BY sequence) AS prev_geom
            FROM ordered
        )
        SELECT COALESCE(SUM(ST_Distance(geom, prev_geom)), 0) AS total_m
        FROM pairs
        WHERE prev_geom IS NOT NULL
    """
    )
    total = db.scalar(stmt, {"route_id": route_id}) or 0.0
    return {"route_id": route_id, "meters": float(total)}
