# Simple operational KPIs.

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models
from ..deps import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    today = date.today()

    total_shipments = db.scalar(select(func.count(models.Shipment.id))) or 0

    in_transit = (
        db.scalar(
            select(func.count(models.Shipment.id)).where(models.Shipment.status == "IN_TRANSIT")
        )
        or 0
    )

    delivered_today = (
        db.scalar(
            select(func.count(models.Shipment.id)).where(
                func.date(models.Shipment.delivered_at) == today
            )
        )
        or 0
    )

    # On-time rate = delivered_at <= planned_delivery_date (among delivered with a plan)
    on_time = (
        db.scalar(
            select(func.count(models.Shipment.id)).where(
                models.Shipment.status == "DELIVERED",
                models.Shipment.planned_delivery_date.is_not(None),
                func.date(models.Shipment.delivered_at) <= models.Shipment.planned_delivery_date,
            )
        )
        or 0
    )

    delivered_with_plan = (
        db.scalar(
            select(func.count(models.Shipment.id)).where(
                models.Shipment.status == "DELIVERED",
                models.Shipment.planned_delivery_date.is_not(None),
            )
        )
        or 0
    )

    on_time_rate = (on_time / delivered_with_plan) if delivered_with_plan else None

    return {
        "total_shipments": total_shipments,
        "in_transit": in_transit,
        "delivered_today": delivered_today,
        "on_time_rate": on_time_rate,
    }
