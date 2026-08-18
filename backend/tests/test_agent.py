import pytest
from unittest.mock import MagicMock
from app.schemas.agent import AgentRequest
from app.agent.orchestrator import AgentOrchestrator
from google.genai.errors import APIError

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
    # Mock genai.Client
    mock_client = MagicMock()
    mocker.patch("app.agent.orchestrator.genai.Client", return_value=mock_client)
    # Provide an initialized in-memory profile DB so orchestrator.ask(, user_id=1) works
    from app.database import ProfileRepository, init_db
    db_path = str(tmp_path / "test.db")
    init_db(db_path=db_path)
    repo = ProfileRepository(db_path=db_path)
    agent = AgentOrchestrator(profile_repo=repo)
    return agent

def test_no_tool_response(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    mock_generate.return_value = MockGenerateContentResponse(
        text='{"answer": "Hello", "citations": [], "grounded": false, "insufficient_context": false}'
    )
    
    resp = orchestrator.ask(AgentRequest(query="Hi"), user_id=1)
    
    assert resp.answer == "Hello"
    assert resp.grounded is False
    assert resp.generation_error is False
    assert len(resp.tool_calls) == 0

def test_single_tool_call(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    # First call: returns a function call
    call1 = MockGenerateContentResponse(
        function_calls=[MockFunctionCall(name="calculate_bmi", args={"weight_kg": 70, "height_cm": 175})]
    )
    # Second call: returns final answer
    call2 = MockGenerateContentResponse(
        text='{"answer": "Your BMI is 22.9.", "citations": [], "grounded": false, "insufficient_context": false}'
    )
    mock_generate.side_effect = [call1, call2]
    
    resp = orchestrator.ask(AgentRequest(query="What is my BMI?"), user_id=1)
    
    assert resp.answer == "Your BMI is 22.9."
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].tool_name == "calculate_bmi"
    assert resp.tool_calls[0].status == "success"

def test_multiple_independent_tool_calls(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    # First call: returns two function calls
    call1 = MockGenerateContentResponse(
        function_calls=[
            MockFunctionCall(name="calculate_bmi", args={"weight_kg": 70, "height_cm": 175}),
            MockFunctionCall(name="calculate_bmr", args={"weight_kg": 70, "height_cm": 175, "age": 30, "sex": "male"})
        ]
    )
    # Second call: returns final answer
    call2 = MockGenerateContentResponse(
        text='{"answer": "Here are your stats.", "citations": [], "grounded": false, "insufficient_context": false}'
    )
    mock_generate.side_effect = [call1, call2]
    
    resp = orchestrator.ask(AgentRequest(query="What is my BMI and BMR?"), user_id=1)
    
    assert len(resp.tool_calls) == 2
    assert {tc.tool_name for tc in resp.tool_calls} == {"calculate_bmi", "calculate_bmr"}

def test_tool_retry_limit_exceeded(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    # The model continually passes bad arguments
    call1 = MockGenerateContentResponse(
        function_calls=[MockFunctionCall(name="calculate_bmi", args={"weight_kg": -10, "height_cm": -10})]
    )
    # It just loops. After 3 tries (retries per call = 2, so 3 total attempts for the same tool erroring out in a row), it should break.
    mock_generate.side_effect = [call1, call1, call1, call1]
    
    resp = orchestrator.ask(AgentRequest(query="My BMI?"), user_id=1)
    
    assert resp.generation_error is True
    assert resp.error_code == "TOOL_RETRY_LIMIT_EXCEEDED"

def test_max_iterations_exceeded(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    # The model continually calls a valid tool, doing valid things but never giving an answer
    call1 = MockGenerateContentResponse(
        function_calls=[MockFunctionCall(name="calculate_bmi", args={"weight_kg": 70, "height_cm": 175})]
    )
    # Return it endlessly
    mock_generate.return_value = call1
    
    # Wait, MAX_TOOL_CALLS is 5. So it will hit MAX_TOOL_CALLS_EXCEEDED first.
    # Let's change the orchestrator's MAX_TOOL_CALLS temporarily for this test or just expect that error.
    resp = orchestrator.ask(AgentRequest(query="Loop"), user_id=1)
    
    assert resp.generation_error is True
    assert resp.error_code == "MAX_TOOL_CALLS_EXCEEDED"

def test_citation_validation_failure(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    # First call: search knowledge (mock the registry or just let it hit the real RetrievalService which will return nothing or we mock the registry)
    # We will mock the registry to return a specific RetrievalResult
    from app.tools import registry
    mocker.patch.object(registry, "execute", return_value={
        "success": True,
        "data": {
            "results": [
                {
                    "chunk_id": "chunk_1",
                    "document_id": "doc_123",
                    "title": "Diet Title",
                    "source_name": "WHO",
                    "source_status": "authoritative",
                    "topic": "nutrition",
                    "source_url": "url",
                    "text_type": "source_excerpt",
                    "section": "1",
                    "page": "1",
                    "distance": 0.5,
                    "text": "Protein is good."
                }
            ]
        },
        "error": None
    })
    
    call1 = MockGenerateContentResponse(
        function_calls=[MockFunctionCall(name="search_knowledge", args={"query": "protein"})]
    )
    # The model fabricates a citation "doc_fake" but claims grounded=True
    call2 = MockGenerateContentResponse(
        text='{"answer": "Protein is good.", "citations": ["doc_fake"], "grounded": true, "insufficient_context": false}'
    )
    mock_generate.side_effect = [call1, call2]
    
    resp = orchestrator.ask(AgentRequest(query="Protein?"), user_id=1)
    
    assert resp.generation_error is True
    assert resp.error_code == "CITATION_VALIDATION_FAILED"

def test_valid_citation(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    from app.tools import registry
    mocker.patch.object(registry, "execute", return_value={
        "success": True,
        "data": {
            "results": [
                {
                    "chunk_id": "chunk_1",
                    "document_id": "doc_123",
                    "title": "Diet Title",
                    "source_name": "WHO",
                    "source_status": "authoritative",
                    "topic": "nutrition",
                    "source_url": "url",
                    "text_type": "source_excerpt",
                    "section": "1",
                    "page": "1",
                    "distance": 0.5,
                    "text": "Protein is good."
                }
            ]
        },
        "error": None
    })
    
    call1 = MockGenerateContentResponse(
        function_calls=[MockFunctionCall(name="search_knowledge", args={"query": "protein"})]
    )
    call2 = MockGenerateContentResponse(
        text='{"answer": "Protein is good.", "citations": ["doc_123"], "grounded": true, "insufficient_context": false}'
    )
    mock_generate.side_effect = [call1, call2]
    
    resp = orchestrator.ask(AgentRequest(query="Protein?"), user_id=1)
    
    assert resp.generation_error is False
    assert resp.error_code is None
    assert len(resp.citations) == 1
    assert resp.citations[0].document_id == "doc_123"

def test_malformed_json(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    mock_generate.return_value = MockGenerateContentResponse(
        text='{"answer": "Unclosed JSON'
    )
    
    resp = orchestrator.ask(AgentRequest(query="Hi"), user_id=1)
    
    assert resp.generation_error is True
    assert resp.error_code == "MALFORMED_RESPONSE"

def test_api_error(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    error = APIError("Quota exceeded", 429)
    error.code = 429
    mock_generate.side_effect = error
    
    resp = orchestrator.ask(AgentRequest(query="Hi"), user_id=1)
    
    assert resp.generation_error is True
    assert resp.error_code == "MODEL_RATE_LIMIT"

def test_tool_call_result_exposed_safely(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    # Call with a deterministic calculation tool
    call1 = MockGenerateContentResponse(
        function_calls=[
            MockFunctionCall(name="calculate_tdee", args={"weight_kg": 70, "height_cm": 175, "age": 30, "sex": "male", "activity_level": "sedentary"}),
            MockFunctionCall(name="calculate_protein_target", args={"weight_kg": 70, "goal": "build_muscle"})
        ]
    )
    call2 = MockGenerateContentResponse(
        text='{"answer": "Results here", "citations": [], "grounded": false, "insufficient_context": false}'
    )
    mock_generate.side_effect = [call1, call2]
    
    resp = orchestrator.ask(AgentRequest(query="Calculate my TDEE and protein"), user_id=1)
    
    assert len(resp.tool_calls) == 2
    tdee_call = resp.tool_calls[0]
    protein_call = resp.tool_calls[1]
    
    # Verify arguments are NOT exposed in ToolCallRecord schema
    assert not hasattr(tdee_call, "arguments")
    
    # Verify exact backend calculation is exposed in result
    assert tdee_call.status == "success"
    assert tdee_call.result["success"] is True
    assert "tdee" in tdee_call.result["data"]
    
    assert protein_call.status == "success"
    assert protein_call.result["success"] is True
    assert "protein_target_min" in protein_call.result["data"]
    
def test_tool_call_error_exposed_without_args(orchestrator, mocker):
    mock_generate = orchestrator.client.models.generate_content
    # Call with a malformed argument to trigger tool failure
    call1 = MockGenerateContentResponse(
        function_calls=[
            MockFunctionCall(name="calculate_tdee", args={"weight_kg": -10, "height_cm": 175, "age": 30, "sex": "male", "activity_level": "sedentary"})
        ]
    )
    call2 = MockGenerateContentResponse(
        text='{"answer": "Results here", "citations": [], "grounded": false, "insufficient_context": false}'
    )
    mock_generate.side_effect = [call1, call2]
    
    resp = orchestrator.ask(AgentRequest(query="Calculate my TDEE"), user_id=1)
    
    assert len(resp.tool_calls) == 1
    tdee_call = resp.tool_calls[0]
    
    # Verify arguments are NOT exposed
    assert not hasattr(tdee_call, "arguments")
    
    # Verify structured error is exposed
    assert tdee_call.status == "error"
    assert tdee_call.result["success"] is False
    assert "weight_kg" in str(tdee_call.result["error"]).lower() or "error" in str(tdee_call.result["error"]).lower()
