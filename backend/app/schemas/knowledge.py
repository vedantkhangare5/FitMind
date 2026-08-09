from typing import List, Optional
from pydantic import BaseModel, Field

class KnowledgeDocument(BaseModel):
    document_id: str = Field(..., description="Unique deterministic ID for this document")
    title: str = Field(..., description="Title of the source document")
    topic: str = Field(..., description="High-level topic (e.g., Protein, Sleep)")
    source_name: str = Field(..., description="Authoritative body (e.g., WHO, NIH)")
    source_url: Optional[str] = Field(None, description="Link to the original source")
    publication_date: Optional[str] = Field(None, description="Publication year or exact date")
    authors: Optional[List[str]] = Field(default_factory=list)
    source_type: Optional[str] = Field(None, description="e.g., official_guideline, position_stand")
    source_status: str = Field(..., description="e.g., active, superseded, historical, test_only")
    supersedes_document_id: Optional[str] = Field(None, description="ID of the document this replaces")
    evidence_level: Optional[str] = Field(None, description="e.g., high, moderate, low")
    retrieved_date: Optional[str] = Field(None, description="Date added to the KB")
    section: Optional[str] = Field(None, description="Section of the document the text comes from")
    page: Optional[str] = Field(None, description="Page number or 'Webpage'")
    text_type: str = Field(
        ..., 
        pattern="^(source_excerpt|editorial_summary)$", 
        description="Whether this is a verbatim quote or a summary"
    )
    text: str = Field(..., description="The actual text content to be chunked")


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    chunk_index: int
    # Inherited metadata for ChromaDB filtering and citation
    source_name: str
    title: str
    topic: str
    section: Optional[str] = None
    page: Optional[str] = None
    source_url: Optional[str] = None
    source_status: str
    text_type: str


class RetrievalResult(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    title: str
    source_name: str
    source_url: str
    source_status: str
    text_type: str
    topic: str
    section: str
    page: str
    distance: float = Field(..., description="Distance score from ChromaDB. Lower is more similar.")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language search query")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")
    topic: Optional[str] = Field(None, description="Optional topic filter")
    source_status: Optional[str] = Field(None, description="Optional status filter")


class SearchResponse(BaseModel):
    query: str
    results: List[RetrievalResult]
