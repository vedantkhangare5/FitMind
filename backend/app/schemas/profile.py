"""
Pydantic schemas for the fitness profile API.

Response uses a nested structure separating persisted profile data
from derived metrics (which are always calculated fresh from calculators.py).
"""

from pydantic import BaseModel, Field


class ProfileData(BaseModel):
    """The raw persisted profile fields — exactly what is stored in SQLite."""
    age: int
    sex: str
    height_cm: float
    weight_kg: float
    activity_level: str
    goal: str


class DerivedMetrics(BaseModel):
    """Calculated on every read from the current profile. Never stored."""
    bmi: float
    bmi_category: str
    bmr: int
    tdee: int
    calorie_target: int
    protein_target_min: int
    protein_target_max: int


class FitnessProfileResponse(BaseModel):
    """
    Full profile response: persisted data + freshly calculated derived metrics.
    
    Structure:
    {
        "profile": { age, sex, height_cm, weight_kg, activity_level, goal },
        "updated_at": "...",
        "derived_metrics": { bmi, bmi_category, bmr, tdee, ... }
    }
    """
    profile: ProfileData
    updated_at: str
    derived_metrics: DerivedMetrics
