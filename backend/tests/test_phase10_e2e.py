import pytest
from fastapi.testclient import TestClient
from app.main import app
import os
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.agent.orchestrator.genai.Client")
def test_e2e_successful_turn(mock_client_class):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.function_calls = []
    mock_resp.text = '{"answer": "Here is the summary.", "citations": [], "grounded": false, "insufficient_context": false}'
    mock_client.models.generate_content.return_value = mock_resp
    mock_client_class.return_value = mock_client
    
    response = client.post("/api/agent/ask", json={"query": "How is my progress?"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Here is the summary."
    assert data["generation_error"] is False
    assert "total_duration_ms" in data
    assert type(data["total_duration_ms"]) is int

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.agent.orchestrator.genai.Client")
def test_e2e_rate_limit(mock_client_class):
    from google.genai.errors import APIError
    
    mock_client = MagicMock()
    error = APIError(429, {"error": "Rate limit"})
    mock_client.models.generate_content.side_effect = error
    mock_client_class.return_value = mock_client
    
    response = client.post("/api/agent/ask", json={"query": "Hello"})
    
    # It returns 200 with generation_error=True (soft error for frontend handling)
    assert response.status_code == 200
    data = response.json()
    assert data["generation_error"] is True
    assert data["error_code"] == "MODEL_RATE_LIMIT"
    assert "total_duration_ms" in data
