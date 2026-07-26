from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# Document Schemas
class DocumentBase(BaseModel):
    filename: str
    total_pages: int = 0
    total_chunks: int = 0
    processing_status: str = "PENDING"
    category: str = "Unclassified"
    category_confidence: float = 0.0

class DocumentResponse(DocumentBase):
    id: str
    upload_timestamp: datetime

    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total_count: int

# Search Schemas
class SearchQuery(BaseModel):
    query: str
    document_ids: Optional[List[str]] = None
    search_mode: str = Field(default="hybrid", description="keyword, semantic, or hybrid")
    top_k: int = Field(default=5, ge=1, le=20)

class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    document_name: str
    page_number: int
    text: str
    score: float
    search_mode: str

class SearchResponse(BaseModel):
    query: str
    search_mode: str
    total_results: int
    results: List[SearchResultItem]

# Assistant / QA Schemas
class QuestionRequest(BaseModel):
    session_id: str
    question: str
    document_ids: Optional[List[str]] = None

class Citation(BaseModel):
    document_id: str
    document_name: str
    page_number: int
    snippet: str

class QuestionResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    citations: List[Citation]
    retrieved_contexts: List[SearchResultItem]
    confidence_score: float
    status: str  # "SUCCESS" or "UNANSWERABLE"

# Document Comparison Schemas
class CompareRequest(BaseModel):
    document_ids: List[str] = Field(..., min_items=2)
    aspects: Optional[List[str]] = None  # e.g., ["methodology", "pros_cons", "conclusions"]

class ComparisonAspect(BaseModel):
    aspect_name: str
    comparison_text: str

class CompareResponse(BaseModel):
    document_ids: List[str]
    document_names: List[str]
    matrix: List[ComparisonAspect]
    executive_comparison: str

# Document Summarization Schemas
class SummarizeRequest(BaseModel):
    document_id: str

class SummarizeResponse(BaseModel):
    document_id: str
    document_name: str
    executive_summary: str
    technical_summary: str
    bullet_points: List[str]
    key_takeaways: List[str]

# Classification Schemas
class ClassificationResponse(BaseModel):
    document_id: str
    document_name: str
    category: str
    confidence: float
    probabilities: Dict[str, float]

# Analytics Schemas
class AnalyticsResponse(BaseModel):
    total_documents: int
    total_chunks: int
    total_embeddings: int
    total_questions_answered: int
    top_queried_documents: List[Dict[str, Any]]
    category_distribution: Dict[str, int]
