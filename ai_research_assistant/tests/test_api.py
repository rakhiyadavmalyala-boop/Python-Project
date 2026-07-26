import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "project" in data

def test_list_documents_endpoint():
    response = client.get("/api/documents")
    assert response.status_code == 200
    data = response.json()
    assert "documents" in data
    assert "total_count" in data

def test_analytics_endpoint():
    response = client.get("/api/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "total_chunks" in data
    assert "total_questions_answered" in data

def test_search_endpoint():
    response = client.post(
        "/api/search",
        json={"query": "machine learning optimization", "search_mode": "hybrid", "top_k": 3}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["search_mode"] == "hybrid"
    assert "results" in data
