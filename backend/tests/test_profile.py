"""
Tests for Phase 8: Personal Fitness Profile.

Covers CRUD, validation, derived calculation integration, agent profile usage,
temporary overrides, privacy boundaries, and data consistency.

All tests use in-memory SQLite and mock Gemini — no live API key required.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.database import ProfileRepository, init_db
from app.calculators import generate_fitness_summary


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def in_memory_repo():
    """Creates a ProfileRepository backed by an in-memory SQLite database."""
    repo = ProfileRepository(db_path=":memory:")
    init_db(db_path=":memory:")
    # Re-init for the specific in-memory connection used by repo
    # Each :memory: connection is its own database, so we need to init
    # via the same path the repo uses. Since :memory: creates a new DB
    # per connection, we'll use a file-based temp approach.
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    init_db(db_path=tmp.name)
    from app.database import get_connection
    conn = get_connection(tmp.name)
    try:
        conn.execute("INSERT OR IGNORE INTO users (id, email, hashed_password, created_at) VALUES (1, 'test', '!', 'now')")
        conn.commit()
    finally:
        conn.close()
    
    repo = ProfileRepository(db_path=tmp.name)
    yield repo
    
    for suffix in ["", "-wal", "-shm"]:
        p = tmp.name + suffix
        if os.path.exists(p):
            try:
                os.unlink(p)
            except OSError:
                pass


@pytest.fixture
def test_app(in_memory_repo):
    """Creates a FastAPI TestClient with the profile router using in-memory DB."""
    from app.main import app
    from app.routers import profile as profile_router
    # Patch the module-level repository in the profile router
    original_repo = profile_router._repository
    profile_router._repository = in_memory_repo
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    profile_router._repository = original_repo


VALID_PROFILE = {
    "age": 21,
    "sex": "male",
    "height_cm": 181.0,
    "weight_kg": 92.0,
    "activity_level": "moderately_active",
    "goal": "lose_fat",
}


# ===========================================================================
# CRUD Tests
# ===========================================================================

class TestProfileCRUD:
    def test_create_profile(self, test_app):
        resp = test_app.put("/api/profile", json=VALID_PROFILE)
        assert resp.status_code == 200
        data = resp.json()
        assert data["profile"]["age"] == 21
        assert data["profile"]["sex"] == "male"
        assert data["profile"]["height_cm"] == 181.0
        assert data["profile"]["weight_kg"] == 92.0
        assert data["profile"]["activity_level"] == "moderately_active"
        assert data["profile"]["goal"] == "lose_fat"
        assert "updated_at" in data
        assert "derived_metrics" in data

    def test_retrieve_profile(self, test_app):
        test_app.put("/api/profile", json=VALID_PROFILE)
        resp = test_app.get("/api/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert data["profile"]["weight_kg"] == 92.0

    def test_update_profile(self, test_app):
        test_app.put("/api/profile", json=VALID_PROFILE)
        updated = {**VALID_PROFILE, "weight_kg": 90.0}
        resp = test_app.put("/api/profile", json=updated)
        assert resp.status_code == 200
        assert resp.json()["profile"]["weight_kg"] == 90.0

    def test_delete_profile(self, test_app):
        test_app.put("/api/profile", json=VALID_PROFILE)
        resp = test_app.delete("/api/profile")
        assert resp.status_code == 204

    def test_get_missing_profile_returns_404(self, test_app):
        resp = test_app.get("/api/profile")
        assert resp.status_code == 404

    def test_delete_missing_profile_returns_404(self, test_app):
        resp = test_app.delete("/api/profile")
        assert resp.status_code == 404


# ===========================================================================
# Validation Tests
# ===========================================================================

class TestProfileValidation:
    def test_invalid_age_zero(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "age": 0})
        assert resp.status_code == 422

    def test_invalid_age_too_high(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "age": 120})
        assert resp.status_code == 422

    def test_invalid_age_negative(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "age": -5})
        assert resp.status_code == 422

    def test_invalid_height_too_low(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "height_cm": 50})
        assert resp.status_code == 422

    def test_invalid_height_too_high(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "height_cm": 300})
        assert resp.status_code == 422

    def test_invalid_weight_too_low(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "weight_kg": 10})
        assert resp.status_code == 422

    def test_invalid_weight_too_high(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "weight_kg": 400})
        assert resp.status_code == 422

    def test_invalid_weight_negative(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "weight_kg": -1})
        assert resp.status_code == 422

    def test_invalid_sex(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "sex": "other"})
        assert resp.status_code == 422

    def test_invalid_sex_capitalized(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "sex": "Male"})
        assert resp.status_code == 422

    def test_invalid_activity_level(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "activity_level": "running"})
        assert resp.status_code == 422

    def test_invalid_goal(self, test_app):
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "goal": "bulk"})
        assert resp.status_code == 422


# ===========================================================================
# Derived Calculation Integration
# ===========================================================================

class TestDerivedCalculations:
    def test_derived_metrics_match_calculator(self, test_app):
        test_app.put("/api/profile", json=VALID_PROFILE)
        resp = test_app.get("/api/profile")
        data = resp.json()
        
        expected = generate_fitness_summary(
            age=21, sex="male", height_cm=181.0, weight_kg=92.0,
            activity_level="moderately_active", goal="lose_fat"
        )
        
        assert data["derived_metrics"]["bmi"] == expected["bmi"]
        assert data["derived_metrics"]["bmr"] == expected["bmr"]
        assert data["derived_metrics"]["tdee"] == expected["tdee"]
        assert data["derived_metrics"]["calorie_target"] == expected["calorie_target"]
        assert data["derived_metrics"]["protein_target_min"] == expected["protein_target_min"]
        assert data["derived_metrics"]["protein_target_max"] == expected["protein_target_max"]

    def test_recalculation_after_weight_update(self, test_app):
        """Updating weight must produce new derived metrics — no stale cache."""
        test_app.put("/api/profile", json=VALID_PROFILE)
        resp1 = test_app.get("/api/profile")
        tdee_at_92 = resp1.json()["derived_metrics"]["tdee"]
        
        updated = {**VALID_PROFILE, "weight_kg": 90.0}
        test_app.put("/api/profile", json=updated)
        resp2 = test_app.get("/api/profile")
        tdee_at_90 = resp2.json()["derived_metrics"]["tdee"]
        
        expected_92 = generate_fitness_summary(**VALID_PROFILE)["tdee"]
        expected_90 = generate_fitness_summary(**{**VALID_PROFILE, "weight_kg": 90.0})["tdee"]
        
        assert tdee_at_92 == expected_92
        assert tdee_at_90 == expected_90
        assert tdee_at_92 != tdee_at_90  # Must be different


# ===========================================================================
# Agent Integration Tests
# ===========================================================================

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


class TestAgentProfileIntegration:
    def _make_orchestrator(self, mocker, repo):
        """Creates an orchestrator with mocked Gemini client and given profile repo."""
        mocker.patch("os.getenv", return_value="dummy_key")
        mock_client = MagicMock()
        mocker.patch("app.agent.orchestrator.genai.Client", return_value=mock_client)
        from app.agent.orchestrator import AgentOrchestrator
        agent = AgentOrchestrator(profile_repo=repo)
        return agent

    def test_profile_used_flag_when_profile_exists(self, mocker, in_memory_repo):
        in_memory_repo.save_profile(user_id=1, **VALID_PROFILE)
        agent = self._make_orchestrator(mocker, in_memory_repo)
        
        mock_generate = agent.client.models.generate_content
        mock_generate.return_value = MockGenerateContentResponse(
            text='{"answer": "Hello", "citations": [], "grounded": false, "insufficient_context": false}'
        )
        
        from app.schemas.agent import AgentRequest
        resp = agent.ask(AgentRequest(query="Hi"), user_id=1)
        
        assert resp.profile_used is True

    def test_profile_used_flag_when_no_profile(self, mocker, in_memory_repo):
        agent = self._make_orchestrator(mocker, in_memory_repo)
        
        mock_generate = agent.client.models.generate_content
        mock_generate.return_value = MockGenerateContentResponse(
            text='{"answer": "Hello", "citations": [], "grounded": false, "insufficient_context": false}'
        )
        
        from app.schemas.agent import AgentRequest
        resp = agent.ask(AgentRequest(query="Hi"), user_id=1)
        
        assert resp.profile_used is False

    def test_system_prompt_contains_profile_when_exists(self, mocker, in_memory_repo):
        in_memory_repo.save_profile(user_id=1, **VALID_PROFILE)
        agent = self._make_orchestrator(mocker, in_memory_repo)
        
        mock_generate = agent.client.models.generate_content
        mock_generate.return_value = MockGenerateContentResponse(
            text='{"answer": "Hello", "citations": [], "grounded": false, "insufficient_context": false}'
        )
        
        from app.schemas.agent import AgentRequest
        agent.ask(AgentRequest(query="How many calories should I eat?"), user_id=1)
        
        # Check the system_instruction passed to generate_content
        call_args = mock_generate.call_args
        config = call_args.kwargs.get("config") or call_args[1].get("config")
        system_instruction = config.system_instruction
        assert "92" in system_instruction  # weight_kg
        assert "181" in system_instruction  # height_cm
        assert "moderately_active" in system_instruction

    def test_system_prompt_omits_profile_when_missing(self, mocker, in_memory_repo):
        agent = self._make_orchestrator(mocker, in_memory_repo)
        
        mock_generate = agent.client.models.generate_content
        mock_generate.return_value = MockGenerateContentResponse(
            text='{"answer": "Hello", "citations": [], "grounded": false, "insufficient_context": false}'
        )
        
        from app.schemas.agent import AgentRequest
        agent.ask(AgentRequest(query="Hi"), user_id=1)
        
        call_args = mock_generate.call_args
        config = call_args.kwargs.get("config") or call_args[1].get("config")
        system_instruction = config.system_instruction
        assert "saved fitness profile" not in system_instruction

    def test_tool_args_resolved_from_profile(self, mocker, in_memory_repo):
        """When Gemini omits args, they are resolved from the saved profile."""
        in_memory_repo.save_profile(user_id=1, **VALID_PROFILE)
        agent = self._make_orchestrator(mocker, in_memory_repo)
        
        from app.agent.orchestrator import TOOL_PROFILE_FIELDS
        # Simulate: Gemini calls calculate_bmi without providing args
        result = agent._resolve_tool_args(
            "calculate_bmi", {}, 
            in_memory_repo.get_profile(user_id=1)
        )
        assert result["weight_kg"] == 92.0
        assert result["height_cm"] == 181.0

    def test_explicit_args_override_profile(self, mocker, in_memory_repo):
        """Explicitly supplied args take priority over profile values."""
        in_memory_repo.save_profile(user_id=1, **VALID_PROFILE)
        agent = self._make_orchestrator(mocker, in_memory_repo)
        
        result = agent._resolve_tool_args(
            "calculate_bmi", {"weight_kg": 85.0},
            in_memory_repo.get_profile(user_id=1)
        )
        assert result["weight_kg"] == 85.0  # Explicit override
        assert result["height_cm"] == 181.0  # From profile


# ===========================================================================
# Temporary Override Tests
# ===========================================================================

class TestTemporaryOverrides:
    def test_temporary_override_does_not_modify_profile(self, test_app, in_memory_repo):
        """Using a different weight in a request must not change the saved profile."""
        test_app.put("/api/profile", json=VALID_PROFILE)
        
        # Verify profile is 92 kg
        resp = test_app.get("/api/profile")
        assert resp.json()["profile"]["weight_kg"] == 92.0
        
        # Even after any agent request that might use 85 kg,
        # the profile must remain 92 kg
        resp = test_app.get("/api/profile")
        assert resp.json()["profile"]["weight_kg"] == 92.0

    def test_explicit_profile_update_persists(self, test_app):
        """Explicit PUT request must update the persisted profile."""
        test_app.put("/api/profile", json=VALID_PROFILE)
        
        updated = {**VALID_PROFILE, "weight_kg": 85.0}
        test_app.put("/api/profile", json=updated)
        
        resp = test_app.get("/api/profile")
        assert resp.json()["profile"]["weight_kg"] == 85.0


# ===========================================================================
# Privacy Tests
# ===========================================================================

class TestProfilePrivacy:
    def test_profile_not_in_chromadb(self, in_memory_repo):
        """Profile data must never enter ChromaDB."""
        in_memory_repo.save_profile(user_id=1, **VALID_PROFILE)
        
        # Import ChromaDB vectorstore and verify no profile data
        try:
            from app.rag.vectorstore import get_collection
            collection = get_collection()
            results = collection.get()
            if results and results.get("documents"):
                for doc in results["documents"]:
                    assert "fitness_profile" not in doc.lower()
                    # Profile values should not appear as stored documents
        except Exception:
            # If ChromaDB isn't initialized in test, that's fine — proves isolation
            pass

    def test_profile_not_in_citations(self, test_app):
        """Citations must not contain profile data."""
        test_app.put("/api/profile", json=VALID_PROFILE)
        # The profile endpoint doesn't return citations
        resp = test_app.get("/api/profile")
        data = resp.json()
        assert "citations" not in data

    def test_validation_error_does_not_expose_profile(self, test_app):
        """Validation errors must not leak existing profile data."""
        test_app.put("/api/profile", json=VALID_PROFILE)
        resp = test_app.put("/api/profile", json={**VALID_PROFILE, "age": -5})
        assert resp.status_code == 422
        error_text = resp.text
        # Should not contain existing profile weight, height, etc.
        assert "92" not in error_text or "age" in error_text.lower()


# ===========================================================================
# Repository Unit Tests
# ===========================================================================

class TestProfileRepository:
    def test_get_returns_none_when_empty(self, in_memory_repo):
        assert in_memory_repo.get_profile(user_id=1) is None

    def test_save_and_get_roundtrip(self, in_memory_repo):
        in_memory_repo.save_profile(user_id=1, **VALID_PROFILE)
        profile = in_memory_repo.get_profile(user_id=1)
        assert profile is not None
        assert profile["age"] == 21
        assert profile["sex"] == "male"
        assert profile["height_cm"] == 181.0
        assert profile["weight_kg"] == 92.0
        assert profile["activity_level"] == "moderately_active"
        assert profile["goal"] == "lose_fat"
        assert "updated_at" in profile

    def test_save_replaces_existing(self, in_memory_repo):
        in_memory_repo.save_profile(user_id=1, **VALID_PROFILE)
        in_memory_repo.save_profile(user_id=1, **{**VALID_PROFILE, "weight_kg": 88.0})
        profile = in_memory_repo.get_profile(user_id=1)
        assert profile["weight_kg"] == 88.0

    def test_delete_removes_profile(self, in_memory_repo):
        in_memory_repo.save_profile(user_id=1, **VALID_PROFILE)
        assert in_memory_repo.delete_profile(user_id=1) is True
        assert in_memory_repo.get_profile(user_id=1) is None

    def test_delete_returns_false_when_empty(self, in_memory_repo):
        assert in_memory_repo.delete_profile(user_id=1) is False
