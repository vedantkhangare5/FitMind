import pytest
from unittest.mock import patch, MagicMock
from app.agent.orchestrator import AgentOrchestrator
from app.schemas.agent import AgentRequest
from google.genai.errors import APIError

@patch("app.agent.orchestrator.genai.Client")
def test_rate_limit_handling(mock_client_class):
    mock_client = MagicMock()
    # Simulate rate limit
    error = APIError(429, {"error": "Rate limit"})
    mock_client.models.generate_content.side_effect = error
    mock_client_class.return_value = mock_client
    
    agent = AgentOrchestrator(profile_repo=MagicMock())
    
    res = agent.ask(AgentRequest(query="Hello"), user_id=1)
    
    assert res.generation_error is True
    assert res.error_code == "MODEL_RATE_LIMIT"

@patch("app.agent.orchestrator.genai.Client")
def test_api_error_handling(mock_client_class):
    mock_client = MagicMock()
    # Simulate internal server error
    error = APIError(500, {"error": "Internal server error"})
    mock_client.models.generate_content.side_effect = error
    mock_client_class.return_value = mock_client
    
    agent = AgentOrchestrator(profile_repo=MagicMock())
    
    res = agent.ask(AgentRequest(query="Hello"), user_id=1)
    
    assert res.generation_error is True
    assert res.error_code == "API_ERROR"

@patch("app.agent.orchestrator.genai.Client")
def test_malformed_json_response(mock_client_class):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.function_calls = []
    # Missing citations field, which is required
    mock_resp.text = 'this is not valid json'
    mock_client.models.generate_content.return_value = mock_resp
    mock_client_class.return_value = mock_client
    
    agent = AgentOrchestrator(profile_repo=MagicMock())
    
    res = agent.ask(AgentRequest(query="Hello"), user_id=1)
    
    assert res.generation_error is True
    assert res.error_code == "MALFORMED_RESPONSE"

@patch("app.agent.orchestrator.genai.Client")
def test_tool_retry_limit_exceeded(mock_client_class):
    mock_client = MagicMock()
    mock_resp = MagicMock()
    
    class MockCall:
        def __init__(self, name, args):
            self.name = name
            self.args = args
            
    # Continually calling a non-existent tool
    mock_resp.function_calls = [MockCall(name="non_existent_tool", args={})]
    mock_resp.text = ""
    mock_client.models.generate_content.return_value = mock_resp
    mock_client_class.return_value = mock_client
    
    agent = AgentOrchestrator(profile_repo=MagicMock())
    
    res = agent.ask(AgentRequest(query="Hello"), user_id=1)
    
    assert res.generation_error is True
    assert res.error_code == "TOOL_RETRY_LIMIT_EXCEEDED"
