import logging
from typing import Dict, Any

from app.database import BehaviorRepository
from app.calculators import calculate_bmr, calculate_tdee, calculate_calorie_target, calculate_protein_target
from app.database import ProfileRepository

logger = logging.getLogger(__name__)

def execute_get_behavior_summary(user_id: int) -> Dict[str, Any]:
    """
    Retrieves the 7-day behavior summary for the given user, based on their saved profile targets.
    """
    try:
        profile_repo = ProfileRepository()
        profile = profile_repo.get_profile(user_id)
        if not profile:
            return {"error": "User does not have a saved fitness profile, cannot calculate targets for adherence."}
            
        bmr = calculate_bmr(
            weight_kg=profile["weight_kg"],
            height_cm=profile["height_cm"],
            age=profile["age"],
            sex=profile["sex"]
        )
        tdee = calculate_tdee(bmr, profile["activity_level"])
        target_calories = calculate_calorie_target(tdee, profile["goal"])
        target_protein, _ = calculate_protein_target(profile["weight_kg"], profile["goal"])
        
        behavior_repo = BehaviorRepository()
        summary = behavior_repo.get_summary(
            user_id=user_id,
            target_calories=target_calories,
            target_protein=target_protein
        )
        
        return summary
    except Exception as e:
        logger.error(f"Error executing get_behavior_summary: {e}")
        return {"error": "Failed to retrieve behavior summary."}
