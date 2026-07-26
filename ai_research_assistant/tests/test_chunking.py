import pytest
from app.services.chunking_service import ChunkingService

def test_recursive_chunking_size_and_overlap():
    chunker = ChunkingService(chunk_size=100, chunk_overlap=20)
    pages = [
        {"page_number": 1, "text": "This is page 1. " * 10},
        {"page_number": 2, "text": "This is page 2 with some detailed text. " * 8}
    ]

    chunks = chunker.chunk_document_pages("doc-123", pages)

    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk["document_id"] == "doc-123"
        assert chunk["page_number"] in [1, 2]
        assert len(chunk["text"]) <= 120  # Allows slight margin for word boundary
        assert "chunk_index" in chunk
        assert "start_char" in chunk
        assert "end_char" in chunk

def test_empty_page_handling():
    chunker = ChunkingService(chunk_size=200, chunk_overlap=30)
    pages = [{"page_number": 1, "text": "   \n\n  "}]

    chunks = chunker.chunk_document_pages("doc-empty", pages)
    assert len(chunks) == 0
