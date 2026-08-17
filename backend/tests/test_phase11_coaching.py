import pytest
from unittest.mock import patch, MagicMock
from app.agent.orchestrator import AgentOrchestrator
from app.schemas.agent import CoachRequest, AgentRequest
from app.database import ProfileRepository, init_db

@pytest.fixture
def test_profile():
    return {
        "age": 30,
        "sex": "male",
        "height_cm": 180,
        "weight_kg": 92,
        "activity_level": "sedentary",
        "goal": "lose_fat"
    }

class MockCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

def test_hypothetical_regression(test_profile, tmp_path):
    """
    Test that a hypothetical query does not mutate the stored profile,
    and a subsequent coaching summary uses the actual profile value.
    """
    db_file = str(tmp_path / "test.db")
    repo = ProfileRepository(db_path=db_file)
    init_db(db_path=db_file)
    repo.save_profile(**test_profile)

    with patch("app.agent.orchestrator.ProgressRepository") as MockProgressRepo, \
         patch("app.agent.orchestrator.BehaviorRepository") as MockBehaviorRepo:
        mock_progress_instance = MockProgressRepo.return_value
        mock_progress_instance.get_summary.return_value = {
            "current_weight": 92,
            "starting_weight": 92,
            "total_change_kg": 0,
            "percentage_change": 0,
            "trend": "stable",
            "entries_count": 1,
            "note": None
        }
        
        mock_behavior_instance = MockBehaviorRepo.return_value
        mock_behavior_instance.get_summary.return_value = {}

        # 1. Ask a hypothetical chat question
        chat_orchestrator = AgentOrchestrator(mode="chat", profile_repo=repo)
        
        mock_client = MagicMock()
        
        # First response: call tool calculate_tdee with 85kg
        mock_response1 = MagicMock()
        mock_response1.function_calls = [MockCall(name="calculate_tdee", args={"weight_kg": 85, "height_cm": 180, "age": 30, "sex": "male", "activity_level": "sedentary"})]
        mock_part1 = MagicMock()
        mock_part1.content = MagicMock()
        mock_response1.candidates = [mock_part1]
        mock_response1.text = ""
        
        # Second response: final JSON answer
        mock_response2 = MagicMock()
        mock_response2.function_calls = []
        mock_response2.text = '{"answer": "Your hypothetical TDEE is 2300.", "citations": [], "grounded": false, "insufficient_context": false}'
        
        mock_client.models.generate_content.side_effect = [mock_response1, mock_response2]
        chat_orchestrator.client = mock_client
        
        chat_req = AgentRequest(query="What would my TDEE be if I weighed 85 kg?")
        chat_resp = chat_orchestrator.ask(chat_req)
        
        assert chat_resp.generation_error is False
        assert len(chat_resp.tool_calls) == 1
        assert chat_resp.tool_calls[0].tool_name == "calculate_tdee"
        
        # Verify the profile is unchanged
        saved_profile = repo.get_profile()
        assert saved_profile["weight_kg"] == 92
        
        # 2. Ask for a coaching summary
        coach_orchestrator = AgentOrchestrator(mode="coach", profile_repo=repo)
        
        mock_client_coach = MagicMock()
        
        mock_response_coach = MagicMock()
        mock_response_coach.function_calls = []
        mock_response_coach.text = '{"summary": "Keep going.", "current_status": "Losing fat", "recommendations": [], "insufficient_context": false}'
        
        mock_client_coach.models.generate_content.return_value = mock_response_coach
        coach_orchestrator.client = mock_client_coach
        
        coach_req = CoachRequest(query=None)
        coach_resp = coach_orchestrator.ask(coach_req)
        
        assert coach_resp.generation_error is False
        assert coach_resp.metrics["tdee"] > 0

def test_coaching_citation_validation(test_profile, tmp_path):
    """
    Test that hallucinated evidence_ids in recommendations trigger an error.
    """
    db_file = str(tmp_path / "test2.db")
    repo = ProfileRepository(db_path=db_file)
    init_db(db_path=db_file)
    repo.save_profile(**test_profile)
    
    with patch("app.agent.orchestrator.ProgressRepository") as MockProgressRepo, \
         patch("app.agent.orchestrator.BehaviorRepository") as MockBehaviorRepo:
        mock_progress_instance = MockProgressRepo.return_value
        mock_progress_instance.get_summary.return_value = {}
        
        mock_behavior_instance = MockBehaviorRepo.return_value
        mock_behavior_instance.get_summary.return_value = {}
        
        orchestrator = AgentOrchestrator(mode="coach", profile_repo=repo)
        
        mock_client = MagicMock()
        
        mock_response = MagicMock()
        mock_response.function_calls = []
        mock_response.text = '{"summary": "Sum", "current_status": "Stat", "recommendations": [{"title": "Rec", "description": "Desc", "priority": "high", "evidence_ids": ["doc-fake-123"]}], "insufficient_context": false}'
        
        mock_client.models.generate_content.return_value = mock_response
        orchestrator.client = mock_client
        
        resp = orchestrator.ask(CoachRequest(query=None))
        assert resp.generation_error is True
        assert resp.error_code == "CITATION_VALIDATION_FAILED"



