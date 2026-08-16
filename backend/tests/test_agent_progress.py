import pytest
from app.agent.orchestrator import AgentOrchestrator
from app.schemas.agent import AgentRequest
from app.database import ProfileRepository, ProgressRepository, get_connection, CREATE_PROFILE_TABLE, CREATE_PROGRESS_TABLE
import os

@pytest.fixture(autouse=True)
def setup_teardown_db():
    db_path = "test_agent_progress.db"
    os.environ["FITMIND_DB_PATH"] = db_path
    
    conn = get_connection(db_path)
    conn.execute(CREATE_PROFILE_TABLE)
    conn.execute(CREATE_PROGRESS_TABLE)
    conn.commit()
    conn.close()
    
    yield
    
    if os.path.exists(db_path):
        os.remove(db_path)

@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="Requires GEMINI_API_KEY")
def test_agent_can_fetch_progress_summary():
    # Setup history
    repo = ProgressRepository()
    repo.add_entry(95.0, "2026-08-01T00:00:00Z")
    repo.add_entry(94.0, "2026-08-08T00:00:00Z")
    repo.add_entry(92.0, "2026-08-15T00:00:00Z")
    
    agent = AgentOrchestrator()
    response = agent.ask(AgentRequest(query="What is my current weight trend and how much have I lost?"))
    
    # Verify tool was called
    tool_called = any(call.tool_name == "get_progress_summary" for call in response.tool_calls)
    assert tool_called
    
    # Verify response contains relevant info
    assert "3 kg" in response.answer or "3kg" in response.answer or "3.0" in response.answer
    assert "losing" in response.answer.lower()
