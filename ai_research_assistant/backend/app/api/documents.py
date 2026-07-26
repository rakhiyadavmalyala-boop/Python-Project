import os
import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.db_models import Document, Chunk
from app.models.schemas import DocumentResponse, DocumentListResponse
from app.services.pdf_service import PDFService
from app.services.chunking_service import ChunkingService
from app.services.vector_service import vector_service
from app.services.classifier_service import classifier_service
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/documents", tags=["Documents"])
chunker = ChunkingService()

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload one or more PDF documents, run extraction, intelligent chunking, vector indexing, and TF document classification.
    """
    uploaded_docs = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a PDF.")

        doc_id = str(uuid.uuid4())
        file_path = os.path.join(settings.UPLOADS_DIR, f"{doc_id}_{file.filename}")

        # 1. Save uploaded file to disk
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        # Create DB record
        db_doc = Document(
            id=doc_id,
            filename=file.filename,
            filepath=file_path,
            upload_timestamp=datetime.datetime.utcnow(),
            processing_status="PROCESSING"
        )
        db.add(db_doc)
        db.commit()
        db.refresh(db_doc)

        try:
            # 2. Extract PDF text by page
            pages = PDFService.extract_text_by_page(file_path)
            total_pages = len(pages)
            full_text = "\n".join([p["text"] for p in pages])

            # 3. Intelligent Chunking
            chunk_dicts = chunker.chunk_document_pages(doc_id, pages)
            
            # Attach document filename to chunk metadata
            for c in chunk_dicts:
                c["document_name"] = file.filename

            # 4. Save chunks to DB
            for c in chunk_dicts:
                db_chunk = Chunk(
                    id=c["id"],
                    document_id=doc_id,
                    page_number=c["page_number"],
                    chunk_index=c["chunk_index"],
                    text=c["text"],
                    start_char=c["start_char"],
                    end_char=c["end_char"]
                )
                db.add(db_chunk)

            # 5. Vector Indexing
            vector_service.add_chunks(chunk_dicts)

            # 6. TensorFlow Category Classification
            category, confidence, _ = classifier_service.classify_text(full_text)

            # Update Document DB Record
            db_doc.total_pages = total_pages
            db_doc.total_chunks = len(chunk_dicts)
            db_doc.category = category
            db_doc.category_confidence = confidence
            db_doc.processing_status = "COMPLETED"
            db.commit()
            db.refresh(db_doc)

            # Log analytics event
            analytics_service.log_event(db, "upload", document_id=doc_id)

            uploaded_docs.append(db_doc)

        except Exception as e:
            db_doc.processing_status = "FAILED"
            db.commit()
            raise HTTPException(status_code=500, detail=f"Error processing '{file.filename}': {str(e)}")

    return uploaded_docs

@router.get("", response_model=DocumentListResponse)
def list_documents(db: Session = Depends(get_db)):
    """
    List all uploaded documents with metadata.
    """
    docs = db.query(Document).order_by(Document.upload_timestamp.desc()).all()
    return DocumentListResponse(documents=docs, total_count=len(docs))

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: str, db: Session = Depends(get_db)):
    """
    Retrieve metadata for a specific document.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return doc

@router.delete("/{document_id}")
def delete_document(document_id: str, db: Session = Depends(get_db)):
    """
    Delete a document, its DB records, vector store chunks, and uploaded file.
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Remove file from disk
    if os.path.exists(doc.filepath):
        try:
            os.remove(doc.filepath)
        except Exception:
            pass

    # Purge from vector store
    vector_service.remove_document_chunks(document_id)

    # Delete from DB
    db.delete(doc)
    db.commit()
    return {"message": f"Document '{doc.filename}' successfully deleted."}

@router.post("/{document_id}/reprocess", response_model=DocumentResponse)
def reprocess_document(document_id: str, db: Session = Depends(get_db)):
    """
    Reprocesses document pipeline (extraction, chunking, indexing, classification).
    """
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    # Clear old vector store & DB chunks
    vector_service.remove_document_chunks(document_id)
    db.query(Chunk).filter(Chunk.document_id == document_id).delete()

    # Re-run pipeline
    pages = PDFService.extract_text_by_page(doc.filepath)
    full_text = "\n".join([p["text"] for p in pages])

    chunk_dicts = chunker.chunk_document_pages(document_id, pages)
    for c in chunk_dicts:
        c["document_name"] = doc.filename
        db_chunk = Chunk(
            id=c["id"],
            document_id=document_id,
            page_number=c["page_number"],
            chunk_index=c["chunk_index"],
            text=c["text"],
            start_char=c["start_char"],
            end_char=c["end_char"]
        )
        db.add(db_chunk)

    vector_service.add_chunks(chunk_dicts)

    category, confidence, _ = classifier_service.classify_text(full_text)
    doc.total_pages = len(pages)
    doc.total_chunks = len(chunk_dicts)
    doc.category = category
    doc.category_confidence = confidence
    doc.processing_status = "COMPLETED"
    db.commit()
    db.refresh(doc)

    return doc
