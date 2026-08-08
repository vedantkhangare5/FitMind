import pytest
import os
from unittest.mock import patch, MagicMock

from app.schemas.knowledge import KnowledgeDocument
from app.rag.chunker import split_text, chunk_document
from app.rag.embeddings import EmbeddingService
from app.rag.vectorstore import VectorStore

@pytest.fixture
def sample_document():
    return KnowledgeDocument(
        document_id="test_doc_001",
        title="Test Title",
        topic="Testing",
        source_name="Test Source",
        source_url="http://test",
        publication_date="2026",
        source_type="test",
        source_status="active",
        evidence_level="high",
        retrieved_date="2026-08-08",
        section="intro",
        page="1",
        text_type="editorial_summary",
        text="This is a short test document. " * 50  # ~300 words
    )

def test_split_text_respects_size():
    text = "word " * 100
    # chunk size 50 chars, should split into multiple chunks
    chunks = split_text(text, chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 50

def test_chunk_document_preserves_metadata(sample_document):
    chunks = chunk_document(sample_document, chunk_size=100, chunk_overlap=20)
    
    assert len(chunks) > 0
    # Verify metadata preservation
    assert chunks[0].document_id == "test_doc_001"
    assert chunks[0].source_name == "Test Source"
    assert chunks[0].text_type == "editorial_summary"
    
    # Verify deterministic IDs
    assert chunks[0].chunk_id == "test_doc_001_chunk_0"
    assert chunks[1].chunk_id == "test_doc_001_chunk_1"


@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.rag.embeddings.genai.Client")
def test_embedding_service_mocked(mock_client_class):
    # Mock the genai client response
    mock_client = MagicMock()
    mock_response = MagicMock()
    
    # Fake embedding
    fake_emb = MagicMock()
    fake_emb.values = [0.1, 0.2, 0.3]
    mock_response.embeddings = [fake_emb]
    
    mock_client.models.embed_content.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    service = EmbeddingService()
    embeddings = service.embed_documents(["test text"])
    
    assert len(embeddings) == 1
    assert embeddings[0] == [0.1, 0.2, 0.3]
    mock_client.models.embed_content.assert_called_once()

def test_vectorstore_idempotency(sample_document, tmp_path):
    # Use a temporary directory for ChromaDB so tests don't pollute local storage
    store = VectorStore(persist_directory=str(tmp_path), collection_name="test_col")
    
    chunks = chunk_document(sample_document, chunk_size=100, chunk_overlap=20)
    embeddings = [[0.1] * 768 for _ in chunks] # Fake embeddings
    
    # First insertion
    store.upsert_chunks(chunks, embeddings)
    count1 = store.count()
    assert count1 == len(chunks)
    
    # Second insertion (should overwrite, not duplicate)
    store.upsert_chunks(chunks, embeddings)
    count2 = store.count()
    
    assert count1 == count2
