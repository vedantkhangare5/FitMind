import pytest
import os
from unittest.mock import patch, MagicMock

from app.agent.orchestrator import AgentOrchestrator
from app.schemas.agent import AgentRequest
from app.tools.registry import ToolRegistry
from app.database import ProfileRepository, get_connection, CREATE_PROFILE_TABLE, CREATE_PROGRESS_TABLE

@pytest.fixture(autouse=True)
def setup_teardown_db():
    db_path = "test_phase10_security.db"
    os.environ["FITMIND_DB_PATH"] = db_path
    
    from app.database import init_db
    init_db(db_path)
    conn = get_connection(db_path)
    conn.execute("INSERT OR IGNORE INTO users (id, email, hashed_password, created_at) VALUES (1, 'test', '!', 'now')")
    conn.commit()
    conn.close()
    
    yield
    
    for suffix in ["", "-wal", "-shm"]:
        p = db_path + suffix
        if os.path.exists(p):
            try:
                os.remove(p)
            except OSError:
                pass

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.agent.orchestrator.genai.Client")
def test_agent_cannot_leak_api_key(mock_client_class):
    # Simulate a prompt injection that tries to get the key
    agent = AgentOrchestrator()
    
    prompt = agent._build_system_prompt(user_id=1, profile=None)
    assert "fake_key" not in prompt

def test_code_safety_no_eval_exec():
    # Verify no eval or exec in tool implementations
    import ast
    
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    tools_dir = os.path.join(backend_dir, "app", "tools")
    
    for filename in os.listdir(tools_dir):
        if filename.endswith(".py"):
            with open(os.path.join(tools_dir, filename), "r", encoding="utf-8") as f:
                content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            assert node.func.id not in ["eval", "exec", "__import__"], f"Unsafe call in {filename}"

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.agent.orchestrator.genai.Client")
def test_temporary_override_does_not_persist(mock_client_class):
    repo = ProfileRepository()
    repo.save_profile(user_id=1, age=30, sex="male", height_cm=180, weight_kg=80, activity_level="sedentary", goal="lose_fat")
    
    agent = AgentOrchestrator()
    
    # Simulate asking with a different weight
    mock_client = MagicMock()
    mock_response = MagicMock()
    
    class MockCall:
        def __init__(self, name, args):
            self.name = name
            self.args = args
            
    # Model uses 85kg in tool call
    mock_response.function_calls = [MockCall(name="calculate_bmi", args={"weight_kg": 85.0, "height_cm": 180.0})]
    mock_response.text = ""
    
    # Second turn gives answer
    mock_response2 = MagicMock()
    mock_response2.function_calls = []
    mock_response2.text = '{"answer": "Ok", "citations": [], "grounded": false, "insufficient_context": false}'
    
    mock_client.models.generate_content.side_effect = [mock_response, mock_response2]
    mock_client_class.return_value = mock_client
    
    agent.ask(AgentRequest(query="What if I weighed 85 kg?"), user_id=1)
    
    # Verify profile weight is still 80
    profile = repo.get_profile(user_id=1)
    assert profile["weight_kg"] == 80.0

@patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
@patch("app.agent.orchestrator.genai.Client")
def test_infinite_loop_termination(mock_client_class):
    mock_client = MagicMock()
    mock_response = MagicMock()
    
    class MockCall:
        def __init__(self, name, args):
            self.name = name
            self.args = args
            
    # Model keeps asking for tool
    mock_response.function_calls = [MockCall(name="calculate_bmi", args={"weight_kg": 80.0, "height_cm": 180.0})]
    mock_response.text = ""
    
    mock_client.models.generate_content.return_value = mock_response
    mock_client_class.return_value = mock_client
    
    agent = AgentOrchestrator()
    
    with patch("app.agent.orchestrator.registry.execute") as mock_exec:
        mock_exec.return_value = {"success": True, "data": {"result": 25.0}}
        res = agent.ask(AgentRequest(query="Loop"), user_id=1)
        
        assert res.generation_error is True
        assert res.error_code == "MAX_TOOL_CALLS_EXCEEDED"

def test_progress_tool_executes_safely():
    from app.tools.progress import execute_get_progress_summary
    from app.database import ProgressRepository
    
    # Verify function executes with no arguments correctly now
    repo = ProgressRepository()
    repo.add_entry(1, 90.0,  "2026-08-01T00:00:00Z")
    
    result = execute_get_progress_summary(user_id=1)
    assert result["entries_count"] == 1
    
    # ToolRegistry execution
    from app.tools import registry
    result2 = registry.execute("get_progress_summary", {"user_id": 1})
    assert result2["success"] is True
    assert result2["data"]["entries_count"] == 1
