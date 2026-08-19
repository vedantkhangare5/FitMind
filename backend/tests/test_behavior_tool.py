import pytest
from unittest.mock import patch, MagicMock
from app.tools.behavior import execute_get_behavior_summary

@patch("app.tools.behavior.ProfileRepository")
def test_behavior_tool_missing_profile(mock_profile_repo_class):
    """Test that the tool handles users without a profile safely."""
    mock_repo = MagicMock()
    mock_repo.get_profile.return_value = None
    mock_profile_repo_class.return_value = mock_repo
    
    result = execute_get_behavior_summary(999)
    assert "error" in result
    assert "User does not have a saved fitness profile" in result["error"]

@patch("app.tools.behavior.ProfileRepository")
@patch("app.tools.behavior.BehaviorRepository")
def test_behavior_tool_success(mock_behavior_repo_class, mock_profile_repo_class):
    """Test that the tool returns the correct behavior summary."""
    mock_profile_repo = MagicMock()
    mock_profile_repo.get_profile.return_value = {
        "age": 30,
        "sex": "male",
        "height_cm": 180,
        "weight_kg": 80,
        "activity_level": "moderately_active",
        "goal": "lose_fat"
    }
    mock_profile_repo_class.return_value = mock_profile_repo
    
    mock_behavior_repo = MagicMock()
    mock_behavior_repo.get_summary.return_value = {
        "nutrition": {"adherence": "High"},
        "workouts": {"total_minutes": 120},
        "days_covered": 7
    }
    mock_behavior_repo_class.return_value = mock_behavior_repo
    
    result = execute_get_behavior_summary(1)
    
    assert "nutrition" in result
    assert "workouts" in result
    assert result["days_covered"] == 7
