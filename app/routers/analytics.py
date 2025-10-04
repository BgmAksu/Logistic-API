# Simple operational KPIs.

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..deps import get_db
from ..services.analytics import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])
service = AnalyticsService()


@router.get("/kpis")
def kpis(db: Session = Depends(get_db)):
    return service.kpis(db)
