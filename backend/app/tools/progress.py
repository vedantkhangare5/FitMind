from typing import Any, Dict
from app.database import ProgressRepository, ProfileRepository

def execute_get_progress_summary(user_id: int, **kwargs) -> Dict[str, Any]:
    """
    Executes the get_progress_summary tool.
    Returns the deterministic progress summary.
    """
    profile_repo = ProfileRepository()
    progress_repo = ProgressRepository()

    profile = profile_repo.get_profile(user_id)
    goal = profile["goal"] if profile else None

    summary = progress_repo.get_summary(user_id, goal=goal)
    return summary
