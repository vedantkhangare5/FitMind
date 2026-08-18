import pytest
from unittest.mock import patch, MagicMock
from app.agent.orchestrator import AgentOrchestrator
from app.schemas.agent import AgentRequest, CoachRequest
from google.genai import types

@patch("app.agent.orchestrator.genai.Client")
def test_regression_schema_chat_mode(mock_client_class):
    # Setup mock client
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    orchestrator = AgentOrchestrator(mode="chat")
    
    # Mock the LLM returning the CORRECT canonical schema enforced by response_schema
    mock_response = MagicMock()
    mock_response.function_calls = None
    mock_response.text = '{"answer": "Here is your progress.", "citations": [], "grounded": false, "insufficient_context": false}'
    
    mock_client.models.generate_content.return_value = mock_response
    
    req = AgentRequest(query="What is my progress?")
    res = orchestrator.ask(req, user_id=1)
    
    # Validation should succeed
    assert res.generation_error is False
    assert res.error_code is None
    assert res.answer == "Here is your progress."

@patch("app.agent.orchestrator.genai.Client")
def test_regression_schema_coach_mode(mock_client_class):
    # Setup mock client
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    orchestrator = AgentOrchestrator(mode="coach")
    
    # Mock the LLM returning the CORRECT canonical Coach schema
    mock_response = MagicMock()
    mock_response.function_calls = None
    mock_response.text = '{"summary": "Coach summary", "current_status": "Doing great", "recommendations": [], "insufficient_context": false}'
    
    mock_client.models.generate_content.return_value = mock_response
    
    req = CoachRequest()
    res = orchestrator.ask(req, user_id=1)
    
    # Validation should succeed
    assert res.generation_error is False
    assert res.error_code is None
    assert res.summary == "Coach summary"

@patch("app.agent.orchestrator.genai.Client")
def test_regression_malformed_response(mock_client_class):
    # Setup mock client
    mock_client = MagicMock()
    mock_client_class.return_value = mock_client
    
    orchestrator = AgentOrchestrator(mode="chat")
    
    # Mock the LLM returning the BAD schema (e.g., if structured outputs failed)
    mock_response = MagicMock()
    mock_response.function_calls = None
    mock_response.text = '{"response": "This is wrong", "sufficient_context": false}'
    
    mock_client.models.generate_content.return_value = mock_response
    
    req = AgentRequest(query="What is my progress?")
    res = orchestrator.ask(req, user_id=1)
    
    # Should catch the ValidationError and return a clean error code without exposing raw error
    assert res.generation_error is True
    assert res.error_code == "MALFORMED_RESPONSE"
    assert "An error occurred" in res.answer
