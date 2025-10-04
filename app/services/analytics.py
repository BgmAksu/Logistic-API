from dataclasses import dataclass
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models


@dataclass
class AnalyticsService:
    """Read-only aggregations for KPIs."""

    def kpis(self, db: Session) -> dict:
        total = db.scalar(select(func.count(models.Shipment.id))) or 0
        in_transit = (
            db.scalar(select(func.count()).where(models.Shipment.status == "IN_TRANSIT")) or 0
        )
        delivered_today = (
            db.scalar(
                select(func.count()).where(
                    models.Shipment.status == "DELIVERED",
                    func.date(models.Shipment.delivered_at) == date.today(),
                )
            )
            or 0
        )
        # naive on-time rate demo: delivered with planned_delivery_date >= delivered_at::date
        on_time = (
            db.scalar(
                select(func.count()).where(
                    models.Shipment.status == "DELIVERED",
                    models.Shipment.planned_delivery_date.is_not(None),
                    func.date(models.Shipment.delivered_at)
                    <= models.Shipment.planned_delivery_date,
                )
            )
            or 0
        )
        return {
            "total_shipments": int(total),
            "in_transit": int(in_transit),
            "delivered_today": int(delivered_today),
            "on_time_rate": float(on_time) / float(total) if total else 0.0,
        }
