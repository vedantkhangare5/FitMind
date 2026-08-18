import pytest
import sqlite3
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.database import init_db, BehaviorRepository, ProfileRepository
from app.agent.orchestrator import AgentOrchestrator, CoachRequest
from app.schemas.behavior import NutritionLogCreate, WorkoutLogCreate
from pydantic import ValidationError

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    db_file = tmp_path / "test_fitmind.db"
    db_path_str = str(db_file)
    with patch("app.database.get_connection") as mock_conn:
        def mock_get_conn(db_path=None):
            conn = sqlite3.connect(db_path_str)
            conn.row_factory = sqlite3.Row
            return conn
        mock_conn.side_effect = mock_get_conn
        
        init_db(db_path_str)
        conn = mock_get_conn(db_path_str)
        conn.execute("INSERT OR IGNORE INTO users (id, email, hashed_password, created_at) VALUES (1, 'test', '!', 'now')")
        conn.commit()
        conn.close()
        
        yield db_path_str


def test_validation_invalid_dates():
    with pytest.raises(ValidationError):
        NutritionLogCreate(date="2026/08/17", calories=2000, protein_grams=150)
    with pytest.raises(ValidationError):
        WorkoutLogCreate(date="17-08-2026", workout_type="Run", duration_minutes=30, completed=True)

def test_validation_invalid_values():
    with pytest.raises(ValidationError):
        NutritionLogCreate(date="2026-08-17", calories=-100, protein_grams=150)
    with pytest.raises(ValidationError):
        WorkoutLogCreate(date="2026-08-17", workout_type="Run", duration_minutes=-5, completed=True)


def test_crud_and_chronological_ordering(setup_db):
    repo = BehaviorRepository(setup_db)
    repo.log_nutrition(1, "2026-08-16",  2100,  160)
    repo.log_nutrition(1, "2026-08-15",  2000,  150)
    repo.log_nutrition(1, "2026-08-17",  2200,  170)
    
    logs = repo.get_nutrition_logs(user_id=1)
    assert len(logs) == 3
    # Order should be DESC
    assert logs[0]["date"] == "2026-08-17"
    assert logs[1]["date"] == "2026-08-16"
    assert logs[2]["date"] == "2026-08-15"
    
    repo.delete_nutrition_log(1, "2026-08-16")
    assert len(repo.get_nutrition_logs(user_id=1)) == 2

    # Workouts
    repo.log_workout(1, "2026-08-16",  "Lift",  45,  True)
    repo.log_workout(1, "2026-08-17",  "Run",  30,  False)
    
    w_logs = repo.get_workout_logs(user_id=1)
    assert len(w_logs) == 2
    assert w_logs[0]["date"] == "2026-08-17"
    assert w_logs[1]["date"] == "2026-08-16"
    
    repo.delete_workout_log(1, w_logs[0]["id"])
    assert len(repo.get_workout_logs(user_id=1)) == 1


def test_missing_data_and_partial_coverage(setup_db):
    repo = BehaviorRepository(setup_db)
    
    # 7-day window from 2026-08-17 is 2026-08-11 to 2026-08-17
    repo.log_nutrition(1, "2026-08-17",  2000,  150)
    repo.log_nutrition(1, "2026-08-15",  2200,  160)
    # 2 logs out of 7 days
    
    summary = repo.get_summary(user_id=1, today="2026-08-17", target_calories=2100, target_protein=155)
    
    assert summary["window_days"] == 7
    assert summary["nutrition"]["logged_days"] == 2
    # missing days not treated as zero: average should be (2000+2200)/2 = 2100
    assert summary["nutrition"]["avg_calories"] == 2100.0
    assert summary["nutrition"]["avg_protein"] == 155.0
    assert summary["nutrition"]["calorie_adherence"] == 100.0
    
    # 2 out of 7 days is ~28.6% coverage
    assert summary["nutrition"]["coverage"] == 28.6


def test_no_logs(setup_db):
    repo = BehaviorRepository(setup_db)
    summary = repo.get_summary(user_id=1, today="2026-08-17", target_calories=2000)
    
    assert summary["nutrition"]["logged_days"] == 0
    assert summary["nutrition"]["coverage"] == 0.0
    assert summary["nutrition"]["avg_calories"] is None
    assert summary["workouts"]["logged_count"] == 0


def test_workout_targets(setup_db):
    repo = BehaviorRepository(setup_db)
    repo.log_workout(1, "2026-08-15",  "Run",  30,  True)
    repo.log_workout(1, "2026-08-16",  "Run",  30,  True)
    repo.log_workout(1, "2026-08-17",  "Run",  30,  False) # skipped
    
    # Without target
    summary1 = repo.get_summary(user_id=1, today="2026-08-17")
    assert summary1["workouts"]["logged_count"] == 3
    assert summary1["workouts"]["completed_count"] == 2
    assert "target_frequency" not in summary1["workouts"]
    
    # With target
    summary2 = repo.get_summary(user_id=1, today="2026-08-17", target_workouts_per_week=4)
    assert summary2["workouts"]["target_frequency"] == 4
    assert summary2["workouts"]["adherence"] == 50.0  # 2/4 = 50%


@patch("app.database.BehaviorRepository.get_summary")
@patch("app.agent.orchestrator.ProfileRepository.get_profile")
def test_agent_receives_summaries_not_raw(mock_get_profile, mock_get_summary, setup_db):
    # Setup mock returns
    mock_get_profile.return_value = {
        "age": 30, "sex": "male", "height_cm": 175, "weight_kg": 75,
        "activity_level": "sedentary", "goal": "maintain"
    }
    mock_get_summary.return_value = {
        "window_days": 7,
        "nutrition": {"logged_days": 7, "avg_calories": 2000},
        "workouts": {"completed_count": 3}
    }
    
    orchestrator = AgentOrchestrator(mode="coach")
    prompt = orchestrator._build_system_prompt(user_id=1, profile=mock_get_profile.return_value)
    
    # Summary should be injected
    assert "7-day behavioral adherence summary" in prompt
    assert "2000" in prompt
    
    # Agent does not receive raw logs
    assert "nutrition_logs" not in prompt


def test_data_separation(setup_db):
    p_repo = ProfileRepository(setup_db)
    p_repo.save_profile(1, 30, "male", 180, 80, "active", "build_muscle")
    
    b_repo = BehaviorRepository(setup_db)
    b_repo.log_nutrition(1, "2026-08-17",  3000,  200)
    
    # Behavior log shouldn't change the profile
    profile = p_repo.get_profile(user_id=1)
    assert profile["weight_kg"] == 80.0
