from pydantic import BaseModel, Field
from typing import Optional

# Regex for YYYY-MM-DD
DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"

class NutritionLogCreate(BaseModel):
    date: str = Field(..., pattern=DATE_REGEX)
    calories: int = Field(..., gt=0)
    protein_grams: int = Field(..., gt=0)

class NutritionLogResponse(NutritionLogCreate):
    pass

class WorkoutLogCreate(BaseModel):
    date: str = Field(..., pattern=DATE_REGEX)
    workout_type: str = Field(..., min_length=1)
    duration_minutes: int = Field(..., gt=0)
    completed: bool

class WorkoutLogResponse(WorkoutLogCreate):
    id: int
