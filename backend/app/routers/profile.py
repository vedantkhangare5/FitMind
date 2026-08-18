"""
Profile API router.

Provides GET/PUT/DELETE for the single fitness profile.
Derived metrics are always calculated fresh from calculators.py.
"""

import logging
from fastapi import APIRouter, HTTPException, Response, Depends

from app.schemas.fitness import FitnessProfileRequest
from app.schemas.profile import FitnessProfileResponse, ProfileData, DerivedMetrics
from app.database import ProfileRepository
from app.calculators import generate_fitness_summary
from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/profile", tags=["profile"])

# Module-level repository instance.
# Tests can override this via dependency injection or direct patching.
_repository = ProfileRepository()


def _get_repository() -> ProfileRepository:
    return _repository


def _build_response(profile_dict: dict) -> FitnessProfileResponse:
    """Builds a full response with freshly calculated derived metrics."""
    summary = generate_fitness_summary(
        age=profile_dict["age"],
        sex=profile_dict["sex"],
        height_cm=profile_dict["height_cm"],
        weight_kg=profile_dict["weight_kg"],
        activity_level=profile_dict["activity_level"],
        goal=profile_dict["goal"],
    )
    return FitnessProfileResponse(
        profile=ProfileData(
            age=profile_dict["age"],
            sex=profile_dict["sex"],
            height_cm=profile_dict["height_cm"],
            weight_kg=profile_dict["weight_kg"],
            activity_level=profile_dict["activity_level"],
            goal=profile_dict["goal"],
        ),
        updated_at=profile_dict["updated_at"],
        derived_metrics=DerivedMetrics(**summary),
    )


@router.get("", response_model=FitnessProfileResponse)
def get_profile(user_id: int = Depends(get_current_user)):
    """Retrieve the saved profile with freshly calculated derived metrics."""
    repo = _get_repository()
    profile = repo.get_profile(user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="No fitness profile found.")
    return _build_response(profile)


@router.put("", response_model=FitnessProfileResponse)
def save_profile(request: FitnessProfileRequest, user_id: int = Depends(get_current_user)):
    """
    Create or update the fitness profile (upsert).
    
    Validation is handled by FitnessProfileRequest — the same Pydantic schema
    used by the calculator API. No duplicate validation rules.
    """
    repo = _get_repository()
    saved = repo.save_profile(
        user_id=user_id,
        age=request.age,
        sex=request.sex,
        height_cm=request.height_cm,
        weight_kg=request.weight_kg,
        activity_level=request.activity_level,
        goal=request.goal,
    )
    logger.info("Profile upserted successfully.")
    return _build_response(saved)


@router.delete("", status_code=204)
def delete_profile(user_id: int = Depends(get_current_user)):
    """Delete/reset the fitness profile."""
    repo = _get_repository()
    deleted = repo.delete_profile(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="No fitness profile found to delete.")
    return Response(status_code=204)
