# Geospatial endpoints using PostGIS geography functions.

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from ..deps import get_db
from .. import models

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
    from_lat: float, from_lon: float,
    to_lat: float, to_lon: float,
    db: Session = Depends(get_db),
):
    a = func.ST_SetSRID(func.ST_MakePoint(from_lon, from_lat), 4326)
    b = func.ST_SetSRID(func.ST_MakePoint(to_lon, to_lat), 4326)
    d = db.scalar(select(func.ST_Distance(a, b)))
    return {"meters": float(d)}

@router.get("/route-length/{route_id}")
def route_length(route_id: int, db: Session = Depends(get_db)):
    # Sum pairwise distances between consecutive stops (ordered by sequence)
    from sqlalchemy import over
    lag_geom = func.lag(models.Address.geom).over(order_by=models.Stop.sequence)
    stmt = (
        select(func.sum(func.ST_Distance(models.Address.geom, lag_geom)))
        .select_from(models.Stop)
        .join(models.Address, models.Stop.address_id == models.Address.id)
        .where(models.Stop.route_id == route_id, models.Address.geom.is_not(None))
    )
    total = db.scalar(stmt) or 0.0
    return {"route_id": route_id, "meters": float(total)}
