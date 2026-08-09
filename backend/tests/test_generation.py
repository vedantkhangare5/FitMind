import os
import pytest
from unittest.mock import patch, MagicMock
from app.rag.generation import GenerationService, INSUFFICIENT_CONTEXT_MESSAGE
from app.schemas.knowledge import RetrievalResult
from app.schemas.rag import LLMResponseSchema

@pytest.fixture
def mock_retrieval_results():
    return [
        RetrievalResult(
            chunk_id="c1",
            document_id="doc1",
            text="Protein is good.",
            title="T1",
            source_name="S1",
            source_url="U1",
            source_status="active",
            text_type="summary",
            topic="Protein",
            section="Intro",
            page="1",
            distance=0.1
        )
    ]

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.rag.generation.genai.Client")
def test_generate_grounded_answer_success(mock_client_class, mock_retrieval_results):
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Simulate a valid JSON return according to LLMResponseSchema
    mock_response.text = '{"answer": "Protein is beneficial.", "citations": ["doc1"], "grounded": true, "insufficient_context": false}'
    
    mock_client.models.generate_content.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    service = GenerationService()
    res = service.generate_grounded_answer("What about protein?", mock_retrieval_results)
    
    assert res.grounded is True
    assert res.insufficient_context is False
    assert res.answer == "Protein is beneficial."
    assert len(res.citations) == 1
    assert res.citations[0].document_id == "doc1"
    assert res.citations[0].title == "T1"

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.rag.generation.genai.Client")
def test_generate_grounded_answer_insufficient(mock_client_class, mock_retrieval_results):
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Simulate an insufficient context return
    mock_response.text = '{"answer": "I do not know", "citations": [], "grounded": false, "insufficient_context": true}'
    
    mock_client.models.generate_content.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    service = GenerationService()
    res = service.generate_grounded_answer("What about creatine?", mock_retrieval_results)
    
    assert res.insufficient_context is True
    assert res.grounded is False
    assert res.answer == INSUFFICIENT_CONTEXT_MESSAGE
    assert len(res.citations) == 0

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.rag.generation.genai.Client")
def test_generate_grounded_answer_invalid_citations(mock_client_class, mock_retrieval_results):
    mock_client = MagicMock()
    mock_response = MagicMock()
    # Hallucinated citation doc999
    mock_response.text = '{"answer": "Fake news.", "citations": ["doc999"], "grounded": true, "insufficient_context": false}'
    
    mock_client.models.generate_content.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    service = GenerationService()
    res = service.generate_grounded_answer("What about fake?", mock_retrieval_results)
    
    # Grounded but 0 valid citations should flip it to insufficient
    assert res.insufficient_context is True
    assert res.grounded is False
    assert res.answer == INSUFFICIENT_CONTEXT_MESSAGE
    assert len(res.citations) == 0

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.rag.generation.genai.Client")
def test_generate_grounded_answer_api_error(mock_client_class, mock_retrieval_results):
    from google.genai.errors import APIError
    mock_client = MagicMock()
    # Simulate a 429 Rate Limit Error
    error_mock = APIError(429, {})
    mock_client.models.generate_content.side_effect = error_mock
    mock_client_class.return_value = mock_client
    
    service = GenerationService()
    res = service.generate_grounded_answer("What about limits?", mock_retrieval_results)
    
    assert res.insufficient_context is False
    assert res.grounded is False
    assert res.generation_error is True
    assert res.error_code == "MODEL_RATE_LIMIT"

