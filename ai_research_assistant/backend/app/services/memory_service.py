import datetime
import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.db_models import ChatSession, ChatMessage

class MemoryService:
    def get_or_create_session(self, db: Session, session_id: Optional[str] = None) -> ChatSession:
        if not session_id:
            session_id = str(uuid.uuid4())

        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        if not session:
            session = ChatSession(session_id=session_id)
            db.add(session)
            db.commit()
            db.refresh(session)

        return session

    def add_message(
        self,
        db: Session,
        session_id: str,
        role: str,
        content: str,
        citations: Optional[List[Dict[str, Any]]] = None
    ) -> ChatMessage:
        self.get_or_create_session(db, session_id)
        
        msg = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            citations=citations
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    def get_history(self, db: Session, session_id: str, limit: int = 10) -> List[ChatMessage]:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp.asc())
            .limit(limit)
            .all()
        )

    def resolve_coreference(self, db: Session, session_id: str, current_query: str) -> str:
        """
        Resolves pronouns or relative references (e.g. 'its', 'that paper', 'the first document')
        by inspecting recent conversation context.
        """
        history = self.get_history(db, session_id, limit=4)
        if not history:
            return current_query

        query_lower = current_query.lower()
        pronouns = ["its ", "it ", "this paper", "that paper", "the document", "its limitations", "its advantages"]

        if any(p in query_lower for p in pronouns):
            # Extract last user query or assistant mention of a document
            for past_msg in reversed(history):
                if past_msg.citations:
                    first_cit = past_msg.citations[0]
                    doc_name = first_cit.get("document_name", "")
                    if doc_name:
                        return f"{current_query} (referring to {doc_name})"

        return current_query

memory_service = MemoryService()
