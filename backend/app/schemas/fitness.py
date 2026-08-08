"""
Pydantic schemas for the fitness calculation API.
Validates input and structures output.
"""
from typing import List, Optional
from pydantic import BaseModel, Field

class FitnessProfileRequest(BaseModel):
    age: int = Field(..., gt=0, lt=120, description="Age in years")
    sex: str = Field(..., pattern="^(male|female)$", description="Biological sex for BMR calculation")
    height_cm: float = Field(..., gt=50, lt=300, description="Height in centimeters")
    weight_kg: float = Field(..., gt=10, lt=400, description="Weight in kilograms")
    activity_level: str = Field(
        ..., 
        pattern="^(sedentary|lightly_active|moderately_active|very_active|extra_active)$",
        description="Daily activity level"
    )
    goal: str = Field(
        ..., 
        pattern="^(lose_fat|maintain|build_muscle)$",
        description="Primary fitness goal"
    )

class FitnessCalculationResponse(BaseModel):
    bmi: float
    bmi_category: str
    bmr: int
    tdee: int
    calorie_target: int
    protein_target_min: int
    protein_target_max: int
    warnings: List[str] = Field(default_factory=list)
