from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime, timezone

from app.schemas.progress import ProgressEntry, ProgressEntryCreate, ProgressSummary, ProgressHistoryResponse
from app.database import ProgressRepository, ProfileRepository
from app.auth import get_current_user

router = APIRouter(prefix="/api/progress", tags=["progress"])

def get_progress_repo():
    return ProgressRepository()

def get_profile_repo():
    return ProfileRepository()

@router.get("", response_model=ProgressHistoryResponse)
def get_progress_history(
    progress_repo: ProgressRepository = Depends(get_progress_repo),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
    user_id: int = Depends(get_current_user)
):
    """
    Retrieve the full progress history and the deterministic summary.
    """
    entries = progress_repo.get_history(user_id)
    profile = profile_repo.get_profile(user_id)
    goal = profile["goal"] if profile else None
    summary = progress_repo.get_summary(user_id, goal=goal)
    
    return ProgressHistoryResponse(entries=entries, summary=summary)

@router.get("/summary", response_model=ProgressSummary)
def get_progress_summary(
    progress_repo: ProgressRepository = Depends(get_progress_repo),
    profile_repo: ProfileRepository = Depends(get_profile_repo),
    user_id: int = Depends(get_current_user)
):
    """
    Retrieve only the deterministic summary. Useful for the agent.
    """
    profile = profile_repo.get_profile(user_id)
    goal = profile["goal"] if profile else None
    return progress_repo.get_summary(user_id, goal=goal)

@router.post("", response_model=ProgressEntry)
def add_progress_entry(
    entry: ProgressEntryCreate,
    progress_repo: ProgressRepository = Depends(get_progress_repo),
    user_id: int = Depends(get_current_user)
):
    """
    Add a new progress entry.
    """
    recorded_at = entry.recorded_at
    if not recorded_at or not str(recorded_at).strip():
        recorded_at = datetime.now(timezone.utc).isoformat()
    else:
        # Validate ISO 8601
        try:
            parsed = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
            if parsed > datetime.now(timezone.utc):
                raise HTTPException(status_code=400, detail="Cannot record future dates.")
            recorded_at = parsed.isoformat()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ISO-8601 timestamp.")

    new_entry = progress_repo.add_entry(user_id, entry.weight_kg, recorded_at)
    return new_entry

@router.delete("/{entry_id}")
def delete_progress_entry(
    entry_id: int,
    progress_repo: ProgressRepository = Depends(get_progress_repo),
    user_id: int = Depends(get_current_user)
):
    """
    Delete a progress entry by ID.
    """
    deleted = progress_repo.delete_entry(user_id, entry_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Entry not found.")
    return {"message": "Entry deleted successfully"}
