from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone

class ProgressEntryCreate(BaseModel):
    weight_kg: float = Field(..., gt=20.0, lt=500.0, description="Weight in kg must be between 20 and 500")
    recorded_at: Optional[str] = Field(None, description="ISO-8601 timestamp")

class ProgressEntry(BaseModel):
    id: int
    weight_kg: float
    recorded_at: str

class ProgressSummary(BaseModel):
    current_weight: Optional[float]
    starting_weight: Optional[float]
    total_change_kg: Optional[float]
    percentage_change: Optional[float]
    trend: str
    entries_count: int
    note: Optional[str] = None

class ProgressHistoryResponse(BaseModel):
    entries: List[ProgressEntry]
    summary: ProgressSummary
