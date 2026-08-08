from fastapi import APIRouter
from app.schemas.fitness import FitnessProfileRequest, FitnessCalculationResponse
from app.calculators import generate_fitness_summary

router = APIRouter(prefix="/api/fitness", tags=["fitness"])

@router.post("/calculate", response_model=FitnessCalculationResponse)
def calculate_fitness(profile: FitnessProfileRequest):
    """
    Accepts a fitness profile and returns deterministic calculation results.
    This endpoint does not use AI; all logic is deterministic Python.
    """
    result = generate_fitness_summary(
        age=profile.age,
        sex=profile.sex,
        height_cm=profile.height_cm,
        weight_kg=profile.weight_kg,
        activity_level=profile.activity_level,
        goal=profile.goal
    )
    
    return FitnessCalculationResponse(**result)
