from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_db

router = APIRouter(prefix="/api/geo", tags=["geo"])


@router.post("/route/optimize")
def optimize_route(address_ids: list[int], db: Session = Depends(get_db)):
    """
    Demo nearest-neighbor route ordering using PostGIS ST_Distance on geography.
    - Input: list of address IDs (must have geom set)
    - Output: visiting order and total meters.
    """
    if not address_ids:
        raise HTTPException(status_code=400, detail="address_ids cannot be empty")

    # Load only addresses that exist and have geom
    rows = db.execute(
        select(models.Address.id, models.Address.geom).where(
            models.Address.id.in_(address_ids),
            models.Address.geom.is_not(None),
        )
    ).all()

    if len(rows) < 2:
        raise HTTPException(status_code=400, detail="need at least two addresses with geom")

    # Map id -> geography(WKBElement)
    pts: dict[int, object] = {rid: geom for rid, geom in rows}

    # Start at the first given id that exists & has geom
    start = next((aid for aid in address_ids if aid in pts), None)
    if start is None:
        raise HTTPException(status_code=400, detail="no valid address ids with geom found")

    order: list[int] = [start]
    remaining = [aid for aid in address_ids if aid in pts and aid != start]
    total_meters: float = 0.0

    # Greedy nearest-neighbor: from current -> nearest of remaining
    while remaining:
        current = order[-1]
        dists = [
            (
                nxt,
                db.scalar(select(func.ST_Distance(pts[current], pts[nxt]))) or 0.0,
            )
            for nxt in remaining
        ]
        nxt, d = min(dists, key=lambda x: x[1])
        order.append(nxt)
        remaining.remove(nxt)
        total_meters += float(d)

    return {"order": order, "total_meters": total_meters}
