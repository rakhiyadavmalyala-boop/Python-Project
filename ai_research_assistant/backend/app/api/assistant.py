from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.db_models import Document
from app.models.schemas import (
    QuestionRequest, QuestionResponse,
    CompareRequest, CompareResponse,
    SummarizeRequest, SummarizeResponse,
    ClassificationResponse
)
from app.services.rag_service import rag_service
from app.services.comparison_service import comparison_service
from app.services.summarization_service import summarization_service
from app.services.classifier_service import classifier_service
from app.services.memory_service import memory_service
from app.services.analytics_service import analytics_service
from app.services.pdf_service import PDFService

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])

@router.post("/chat", response_model=QuestionResponse)
def chat_question(req: QuestionRequest, db: Session = Depends(get_db)):
    """
    RAG-powered AI Question Answering with page citations and session memory coreference.
    """
    # 1. Coreference query resolution using chat history
    resolved_query = memory_service.resolve_coreference(db, req.session_id, req.question)

    # Save user message to memory
    memory_service.add_message(db, req.session_id, "user", req.question)

    # 2. Execute RAG Question Answering
    response = rag_service.answer_question(
        session_id=req.session_id,
        question=resolved_query,
        document_ids=req.document_ids
    )

    # Convert citations to dict format for storage
    citation_dicts = [c.dict() for c in response.citations]

    # Save assistant response to memory
    memory_service.add_message(db, req.session_id, "assistant", response.answer, citations=citation_dicts)

    # Log analytics
    analytics_service.log_event(db, "question", query=req.question)

    return response

@router.post("/compare", response_model=CompareResponse)
def compare_documents(req: CompareRequest, db: Session = Depends(get_db)):
    """
    Compares methodologies, pros/cons, similarities, and differences across selected documents.
    """
    if len(req.document_ids) < 2:
        raise HTTPException(status_code=400, detail="Please select at least two documents for comparison.")

    docs = db.query(Document).filter(Document.id.in_(req.document_ids)).all()
    doc_names_map = {d.id: d.filename for d in docs}

    response = comparison_service.compare_documents(req.document_ids, doc_names_map)
    analytics_service.log_event(db, "comparison")

    return response

@router.post("/summarize", response_model=SummarizeResponse)
def summarize_document(req: SummarizeRequest, db: Session = Depends(get_db)):
    """
    Generates Executive, Technical, Bullet Point, and Key Takeaway summaries for a document.
    """
    doc = db.query(Document).filter(Document.id == req.document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    response = summarization_service.summarize_document(doc.id, doc.filename)
    analytics_service.log_event(db, "summary", document_id=doc.id)

    return response

@router.post("/classify/{document_id}", response_model=ClassificationResponse)
def classify_document(document_id: str, db: Session = Depends(get_db)):
    """
    Executes TensorFlow document classification model on uploaded document text.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Extract text to classify
    pages = PDFService.extract_text_by_page(doc.filepath)
    full_text = "\n".join([p["text"] for p in pages])

    category, confidence, prob_dict = classifier_service.classify_text(full_text)

    # Update DB record
    doc.category = category
    doc.category_confidence = confidence
    db.commit()

    return ClassificationResponse(
        document_id=doc.id,
        document_name=doc.filename,
        category=category,
        confidence=confidence,
        probabilities=prob_dict
    )
