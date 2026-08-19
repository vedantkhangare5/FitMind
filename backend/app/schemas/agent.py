from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.rag import Citation

class AgentRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)

class ToolCallRecord(BaseModel):
    tool_name: str
    status: str = Field(..., description="'success' or 'error'")
    result: Optional[dict] = None
    duration_ms: Optional[int] = None

class AgentLLMResponse(BaseModel):
    """Schema enforced on the Gemini output via structured outputs."""
    answer: str
    citations: List[str] = Field(..., description="List of document IDs used in the answer")
    grounded: bool
    insufficient_context: bool

class AgentResponse(BaseModel):
    answer: str
    citations: List[Citation]
    tool_calls: List[ToolCallRecord]
    grounded: bool
    insufficient_context: bool
    generation_error: bool = Field(False, description="True if an API, loop limit, or infrastructure error occurred")
    error_code: Optional[str] = Field(None, description="Machine-readable error code if generation_error is true or validation failed")
    profile_used: bool = Field(False, description="True if a saved fitness profile was used for context")
    total_duration_ms: Optional[int] = Field(None, description="Total execution time in milliseconds")

class CoachRequest(BaseModel):
    query: Optional[str] = Field(None, max_length=2000, description="Optional specific coaching question")

class CoachingRecommendation(BaseModel):
    title: str
    description: str
    priority: str = Field(..., description="'high', 'medium', or 'low'")
    evidence_ids: List[str] = Field(default_factory=list, description="List of document IDs from search_knowledge supporting this recommendation (if applicable)")

class CoachLLMResponse(BaseModel):
    """Schema enforced on the Gemini output via structured outputs in coach mode."""
    summary: str
    current_status: str
    recommendations: List[CoachingRecommendation]
    action_plan: List[str] = Field(..., min_length=3, max_length=3, description="Exactly 3 actionable, specific daily tasks based on the user's goal and adherence")
    insufficient_context: bool

class CoachResponse(BaseModel):
    summary: str
    current_status: str
    recommendations: List[CoachingRecommendation]
    action_plan: List[str] = Field(default_factory=list, description="Exactly 3 actionable, specific daily tasks")
    metrics: dict = Field(default_factory=dict, description="Deterministic metrics pre-calculated for the user")
    progress: dict = Field(default_factory=dict, description="Deterministic progress summary")
    behavior: dict = Field(default_factory=dict, description="Deterministic behavioral summary")
    citations: List[Citation]
    tool_calls: List[ToolCallRecord]
    generation_error: bool = Field(False)
    error_code: Optional[str] = Field(None)
    profile_used: bool = Field(False)
    total_duration_ms: Optional[int] = Field(None)

