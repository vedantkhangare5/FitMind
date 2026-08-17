from typing import Any, Dict
from app.database import ProgressRepository, ProfileRepository

def execute_get_progress_summary(**kwargs) -> Dict[str, Any]:
    """
    Executes the get_progress_summary tool.
    Returns the deterministic progress summary.
    """
    profile_repo = ProfileRepository()
    progress_repo = ProgressRepository()

    profile = profile_repo.get_profile()
    goal = profile["goal"] if profile else None

    summary = progress_repo.get_summary(goal=goal)
    return summary
