from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import AnalyticsResponse
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("", response_model=AnalyticsResponse)
def get_analytics(db: Session = Depends(get_db)):
    """
    Returns high-level analytical insights about uploaded documents, total chunks, total embeddings, and search activity.
    """
    return analytics_service.get_system_analytics(db)
