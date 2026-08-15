from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.rag import Citation

class AgentRequest(BaseModel):
    query: str = Field(..., min_length=1)

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
