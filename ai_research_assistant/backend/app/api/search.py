from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import SearchQuery, SearchResponse, SearchResultItem
from app.services.vector_service import vector_service
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("", response_model=SearchResponse)
def search(query_data: SearchQuery, db: Session = Depends(get_db)):
    """
    Search across document knowledge base using Keyword, Semantic, or Hybrid retrieval.
    """
    mode = query_data.search_mode.lower()
    
    if mode == "semantic":
        raw_results = vector_service.search_semantic(
            query=query_data.query,
            document_ids=query_data.document_ids,
            top_k=query_data.top_k
        )
    elif mode == "keyword":
        raw_results = vector_service.search_keyword(
            query=query_data.query,
            document_ids=query_data.document_ids,
            top_k=query_data.top_k
        )
    elif mode == "hybrid":
        raw_results = vector_service.search_hybrid(
            query=query_data.query,
            document_ids=query_data.document_ids,
            top_k=query_data.top_k
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid search_mode. Choose 'keyword', 'semantic', or 'hybrid'.")

    results = [
        SearchResultItem(
            chunk_id=res["id"],
            document_id=res["document_id"],
            document_name=res.get("document_name", "Document"),
            page_number=res["page_number"],
            text=res["text"],
            score=res["score"],
            search_mode=res["search_mode"]
        )
        for res in raw_results
    ]

    analytics_service.log_event(db, "search", query=query_data.query)

    return SearchResponse(
        query=query_data.query,
        search_mode=mode,
        total_results=len(results),
        results=results
    )
