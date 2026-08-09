from typing import List, Optional
from pydantic import BaseModel, Field

class Citation(BaseModel):
    document_id: str
    title: str
    source_name: str
    source_url: Optional[str] = None
    section: Optional[str] = None
    page: Optional[str] = None
    text_type: str

class GenerateRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=50)
    distance_threshold: Optional[float] = Field(
        1.5, 
        description="Maximum allowed distance for a chunk to be considered relevant. Lower means stricter."
    )

class GenerateResponse(BaseModel):
    answer: str
    citations: List[Citation]
    grounded: bool
    insufficient_context: bool
    generation_error: bool = Field(False, description="True if an API or infrastructure error occurred")
    error_code: Optional[str] = Field(None, description="Machine-readable error code if generation_error is true")

class LLMResponseSchema(BaseModel):
    """Schema enforced on the Gemini output via structured outputs."""
    answer: str
    citations: List[str] = Field(..., description="List of document IDs used in the answer")
    grounded: bool
    insufficient_context: bool
