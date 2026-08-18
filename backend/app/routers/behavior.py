from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.schemas.behavior import (
    NutritionLogCreate,
    NutritionLogResponse,
    WorkoutLogCreate,
    WorkoutLogResponse,
)
from app.database import BehaviorRepository, ProfileRepository
from app.calculators import calculate_bmr, calculate_tdee, calculate_calorie_target, calculate_protein_target
from app.auth import get_current_user
import logging

router = APIRouter(prefix="/api/behavior", tags=["Behavior"])
logger = logging.getLogger(__name__)

def get_behavior_repo():
    return BehaviorRepository()

def get_profile_repo():
    return ProfileRepository()

@router.post("/nutrition", response_model=NutritionLogResponse)
def log_nutrition(log: NutritionLogCreate, repo: BehaviorRepository = Depends(get_behavior_repo), user_id: int = Depends(get_current_user)):
    return repo.log_nutrition(user_id, log.date, log.calories, log.protein_grams)

@router.get("/nutrition", response_model=List[NutritionLogResponse])
def get_nutrition_logs(limit: int = 30, repo: BehaviorRepository = Depends(get_behavior_repo), user_id: int = Depends(get_current_user)):
    return repo.get_nutrition_logs(user_id, limit=limit)

@router.delete("/nutrition/{date}")
def delete_nutrition_log(date: str, repo: BehaviorRepository = Depends(get_behavior_repo), user_id: int = Depends(get_current_user)):
    if not repo.delete_nutrition_log(user_id, date):
        raise HTTPException(status_code=404, detail="Nutrition log not found")
    return {"status": "deleted"}

@router.post("/workouts", response_model=WorkoutLogResponse)
def log_workout(log: WorkoutLogCreate, repo: BehaviorRepository = Depends(get_behavior_repo), user_id: int = Depends(get_current_user)):
    return repo.log_workout(user_id, log.date, log.workout_type, log.duration_minutes, log.completed)

@router.get("/workouts", response_model=List[WorkoutLogResponse])
def get_workout_logs(limit: int = 30, repo: BehaviorRepository = Depends(get_behavior_repo), user_id: int = Depends(get_current_user)):
    return repo.get_workout_logs(user_id, limit=limit)

@router.delete("/workouts/{log_id}")
def delete_workout_log(log_id: int, repo: BehaviorRepository = Depends(get_behavior_repo), user_id: int = Depends(get_current_user)):
    if not repo.delete_workout_log(user_id, log_id):
        raise HTTPException(status_code=404, detail="Workout log not found")
    return {"status": "deleted"}

@router.get("/summary")
def get_behavior_summary(
    today: Optional[str] = None,
    repo: BehaviorRepository = Depends(get_behavior_repo),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
    user_id: int = Depends(get_current_user)
):
    profile = profile_repo.get_profile(user_id)
    target_calories = None
    target_protein = None
    target_workouts = None

    if profile:
        bmr = calculate_bmr(
            weight_kg=profile["weight_kg"],
            height_cm=profile["height_cm"],
            age=profile["age"],
            sex=profile["sex"]
        )
        tdee = calculate_tdee(bmr, profile["activity_level"])
        target_calories = calculate_calorie_target(tdee, profile["goal"])
        protein_min, _ = calculate_protein_target(profile["weight_kg"], profile["goal"])
        target_protein = protein_min
    
    return repo.get_summary(
        user_id,
        today=today,
        target_calories=target_calories,
        target_protein=target_protein,
        target_workouts_per_week=target_workouts
    )
