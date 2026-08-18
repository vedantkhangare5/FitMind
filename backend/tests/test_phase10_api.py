import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_malformed_json():
    # Sending plain string instead of JSON
    response = client.post(
        "/api/agent/ask", 
        data="This is not JSON",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422

def test_api_missing_fields():
    # Agent request missing 'query'
    response = client.post("/api/agent/ask", json={})
    assert response.status_code == 422

def test_api_extra_fields_ignored():
    # Pydantic ignores extra fields by default in FastAPI, should return 200/500 depending on agent response, but not 422
    # We mock the orchestrator to avoid hitting gemini
    with pytest.MonkeyPatch.context() as m:
        class MockOrchestrator:
            def ask(self, req, user_id: int):
                from app.schemas.agent import AgentResponse
                return AgentResponse(
                    answer="mock", citations=[], tool_calls=[], grounded=False, 
                    insufficient_context=False, generation_error=False, error_code=None, profile_used=False
                )
        m.setattr("app.routers.agent.AgentOrchestrator", MockOrchestrator)
        
        response = client.post("/api/agent/ask", json={"query": "test", "extra": "field"})
        assert response.status_code == 200
        assert response.json()["answer"] == "mock"

def test_api_invalid_types():
    response = client.put("/api/profile", json={
        "age": "not_an_int",
        "sex": "male",
        "height_cm": 180,
        "weight_kg": 80,
        "activity_level": "sedentary",
        "goal": "lose_fat"
    })
    assert response.status_code == 422

def test_api_extreme_values():
    response = client.put("/api/profile", json={
        "age": 120, # likely rejected by schema
        "sex": "male",
        "height_cm": 180,
        "weight_kg": 80,
        "activity_level": "sedentary",
        "goal": "lose_fat"
    })
    assert response.status_code == 422

def test_api_oversized_string():
    long_string = "a" * 10000
    response = client.post("/api/agent/ask", json={"query": long_string})
    assert response.status_code == 422 # Due to max_length=2000

def test_progress_empty_timestamp():
    response = client.post("/api/progress", json={"weight_kg": 80, "recorded_at": "   "})
    assert response.status_code == 200
    assert "recorded_at" in response.json()
    assert response.json()["recorded_at"] != "   " # Server populated it

def test_error_response_does_not_leak_stack_trace():
    # Simulate internal error
    with pytest.MonkeyPatch.context() as m:
        class MockOrchestrator:
            def ask(self, req, user_id: int):
                raise Exception("Super secret internal error message")
        m.setattr("app.routers.agent.AgentOrchestrator", MockOrchestrator)
        
        response = client.post("/api/agent/ask", json={"query": "test"})
        assert response.status_code == 500
        assert "Super secret internal error message" not in response.text
        assert "Internal server error" in response.text
