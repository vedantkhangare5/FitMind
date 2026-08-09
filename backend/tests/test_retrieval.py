import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.rag.retrieval import RetrievalService
from app.schemas.knowledge import SearchRequest

@patch("app.rag.retrieval.EmbeddingService")
@patch("app.rag.retrieval.VectorStore")
def test_retrieval_service_search(mock_vs_class, mock_emb_class):
    mock_emb = MagicMock()
    mock_emb.embed_query.return_value = [0.1, 0.2]
    mock_emb_class.return_value = mock_emb
    
    mock_vs = MagicMock()
    # ChromaDB query response structure
    mock_vs.search.return_value = {
        "ids": [["chunk_1", "chunk_2"]],
        "documents": [["text 1", "text 2"]],
        "metadatas": [[
            {"document_id": "doc_1", "title": "Doc 1"},
            {"document_id": "doc_2", "title": "Doc 2"}
        ]],
        "distances": [[0.05, 0.15]]
    }
    mock_vs_class.return_value = mock_vs
    
    service = RetrievalService()
    results = service.search("test query", top_k=2)
    
    assert len(results) == 2
    assert results[0].chunk_id == "chunk_1"
    assert results[0].distance == 0.05
    assert results[1].chunk_id == "chunk_2"
    assert results[1].distance == 0.15
    mock_emb.embed_query.assert_called_once_with("test query")
    mock_vs.search.assert_called_once_with(query_embedding=[0.1, 0.2], top_k=2, where=None)

@patch("app.rag.retrieval.RetrievalService")
def test_search_api_endpoint(mock_service_class):
    # Setup mock service
    mock_service = MagicMock()
    
    from app.schemas.knowledge import RetrievalResult
    fake_result = RetrievalResult(
        chunk_id="chunk_1",
        document_id="doc_1",
        text="text",
        title="title",
        source_name="source",
        source_url="url",
        source_status="active",
        text_type="summary",
        topic="topic",
        section="intro",
        page="1",
        distance=0.1
    )
    mock_service.search.return_value = [fake_result]
    
    client = TestClient(app)
    
    # We must override the dependency so it uses our mock
    from app.routers.rag import get_retrieval_service
    app.dependency_overrides[get_retrieval_service] = lambda: mock_service
    
    response = client.post("/api/rag/search", json={"query": "test", "top_k": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test"
    assert len(data["results"]) == 1
    assert data["results"][0]["chunk_id"] == "chunk_1"
    
    mock_service.search.assert_called_once_with(query="test", top_k=5, filters=None)
    
    # Test validation error
    response = client.post("/api/rag/search", json={"query": "", "top_k": 5})
    assert response.status_code == 422
    
    # Clear overrides
    app.dependency_overrides = {}
