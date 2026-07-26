from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.db_models import Document, Chunk, AnalyticsEvent, ChatMessage
from app.models.schemas import AnalyticsResponse

class AnalyticsService:
    def log_event(self, db: Session, event_type: str, document_id: str = None, query: str = None):
        event = AnalyticsEvent(
            event_type=event_type,
            document_id=document_id,
            query=query
        )
        db.add(event)
        db.commit()

    def get_system_analytics(self, db: Session) -> AnalyticsResponse:
        total_documents = db.query(func.count(Document.id)).scalar() or 0
        total_chunks = db.query(func.count(Chunk.id)).scalar() or 0
        total_questions = db.query(func.count(ChatMessage.id)).filter(ChatMessage.role == "user").scalar() or 0

        # Category distribution
        categories = db.query(Document.category, func.count(Document.id)).group_by(Document.category).all()
        cat_dist = {cat: count for cat, count in categories}

        # Top queried documents
        top_docs_query = (
            db.query(AnalyticsEvent.document_id, func.count(AnalyticsEvent.id).label("query_count"))
            .filter(AnalyticsEvent.document_id.isnot(None))
            .group_by(AnalyticsEvent.document_id)
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(5)
            .all()
        )

        top_queried_documents = []
        for doc_id, count in top_docs_query:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                top_queried_documents.append({
                    "document_id": doc.id,
                    "filename": doc.filename,
                    "query_count": count,
                    "category": doc.category
                })

        return AnalyticsResponse(
            total_documents=total_documents,
            total_chunks=total_chunks,
            total_embeddings=total_chunks,  # 1 embedding vector per chunk
            total_questions_answered=total_questions,
            top_queried_documents=top_queried_documents,
            category_distribution=cat_dist
        )

analytics_service = AnalyticsService()
