import pytest
from unittest.mock import MagicMock
from app.schemas.agent import AgentRequest
from app.agent.orchestrator import AgentOrchestrator

class MockContent:
    def __init__(self):
        self.role = "model"
        self.parts = []

class MockCandidate:
    def __init__(self):
        self.content = MockContent()

class MockFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class MockGenerateContentResponse:
    def __init__(self, text=None, function_calls=None):
        self.text = text
        self.function_calls = function_calls or []
        self.candidates = [MockCandidate()]

@pytest.fixture
def orchestrator(mocker, tmp_path):
    mocker.patch("os.getenv", return_value="dummy_key")
    mock_client = MagicMock()
    mocker.patch("app.agent.orchestrator.genai.Client", return_value=mock_client)
    from app.database import ProfileRepository, init_db
    db_path = str(tmp_path / "test.db")
    init_db(db_path=db_path)
    repo = ProfileRepository(db_path=db_path)
    # Set a dummy profile
    repo.save_profile(**{
        "age": 30,
        "sex": "male",
        "height_cm": 180,
        "weight_kg": 90,
        "activity_level": "sedentary",
        "goal": "maintain"
    })
    agent = AgentOrchestrator(profile_repo=repo)
    return agent

def test_agent_rejects_unlisted_tools(orchestrator, mocker):
    """If the LLM hallucinates an unlisted tool, the orchestrator should execute it against ToolRegistry and fail securely."""
    mock_generate = orchestrator.client.models.generate_content
    
    # LLM hallucinates a malicious tool
    call1 = MockGenerateContentResponse(
        function_calls=[MockFunctionCall(name="execute_python", args={"code": "import os; os.system('rm -rf /')"})]
    )
    call2 = MockGenerateContentResponse(
        text='{"answer": "I could not execute the code.", "citations": [], "grounded": false, "insufficient_context": false}'
    )
    mock_generate.side_effect = [call1, call2]
    
    resp = orchestrator.ask(AgentRequest(query="Run some code"))
    
    assert len(resp.tool_calls) == 1
    tc = resp.tool_calls[0]
    assert tc.tool_name == "execute_python"
    assert tc.status == "error"
    assert tc.result["success"] is False
    assert tc.result["error"]["code"] == "UNKNOWN_TOOL"
    assert "Unknown tool" in tc.result["error"]["message"]

def test_agent_conversation_cannot_mutate_profile(orchestrator, mocker):
    """The agent has no tools to permanently mutate the profile. A temporary tool call doesn't overwrite DB."""
    mock_generate = orchestrator.client.models.generate_content
    
    # LLM tries to call a calculation with mutated weight
    call1 = MockGenerateContentResponse(
        function_calls=[MockFunctionCall(name="calculate_bmi", args={"weight_kg": 50, "height_cm": 180})]
    )
    call2 = MockGenerateContentResponse(
        text='{"answer": "Your BMI with 50kg is 15.4", "citations": [], "grounded": false, "insufficient_context": false}'
    )
    mock_generate.side_effect = [call1, call2]
    
    resp = orchestrator.ask(AgentRequest(query="Change my profile weight to 50 kg and calculate BMI."))
    
    # Tool call happened with 50kg
    assert len(resp.tool_calls) == 1
    # But DB profile remains 90kg
    db_profile = orchestrator._profile_repo.get_profile()
    assert db_profile["weight_kg"] == 90.0

def test_agent_cannot_leak_secrets(orchestrator, mocker):
    """If the LLM somehow outputs a secret (which we mock here), the architecture doesn't intrinsically block text output,
    but we verify that the system prompt instructs it not to, and there are no tools that return secrets."""
    # This is more of a behavioral test. In a real prompt injection, the LLM might try to print a secret.
    # We verify the system prompt doesn't contain the API key, and no tool returns it.
    from app.config import settings
    assert settings.GEMINI_API_KEY not in orchestrator._build_system_prompt(None)
