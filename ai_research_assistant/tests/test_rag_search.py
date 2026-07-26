import pytest
from app.services.vector_service import VectorService
from app.services.rag_service import RAGService

def test_vector_search_modes():
    v_service = VectorService()
    sample_chunks = [
        {
            "id": "c1",
            "document_id": "doc1",
            "document_name": "AI Paper.pdf",
            "page_number": 1,
            "chunk_index": 0,
            "text": "Artificial Intelligence agents utilize heuristic A* search algorithms for automated planning.",
            "start_char": 0,
            "end_char": 90
        },
        {
            "id": "c2",
            "document_id": "doc2",
            "document_name": "Cloud Paper.pdf",
            "page_number": 2,
            "chunk_index": 0,
            "text": "Kubernetes orchestration manages Docker microservices across distributed cloud infrastructure.",
            "start_char": 0,
            "end_char": 95
        }
    ]

    v_service.add_chunks(sample_chunks)

    # Test Semantic Search
    sem_res = v_service.search_semantic("heuristic search algorithms", top_k=1)
    assert len(sem_res) == 1
    assert sem_res[0]["document_id"] == "doc1"

    # Test Keyword Search
    kw_res = v_service.search_keyword("Kubernetes Docker", top_k=1)
    assert len(kw_res) == 1
    assert kw_res[0]["document_id"] == "doc2"

    # Test Hybrid Search
    hyb_res = v_service.search_hybrid("heuristic planning", top_k=1)
    assert len(hyb_res) == 1
    assert hyb_res[0]["document_id"] == "doc1"

def test_rag_unanswerable_fallback():
    rag = RAGService()
    # Query non-existent topics when vector store is empty/unmatched
    response = rag.answer_question(
        session_id="test-session",
        question="What is quantum gravity string theory mechanics?"
    )

    assert response.status in ["SUCCESS", "UNANSWERABLE"]
    assert response.question == "What is quantum gravity string theory mechanics?"
