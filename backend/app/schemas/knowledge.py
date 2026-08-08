from typing import List, Optional
from pydantic import BaseModel, Field

class KnowledgeDocument(BaseModel):
    document_id: str = Field(..., description="Unique deterministic ID for this document")
    title: str = Field(..., description="Title of the source document")
    topic: str = Field(..., description="High-level topic (e.g., Protein, Sleep)")
    source_name: str = Field(..., description="Authoritative body (e.g., WHO, NIH)")
    source_url: str = Field(..., description="Link to the original source")
    publication_date: str = Field(..., description="Publication year or exact date")
    authors: List[str] = Field(default_factory=list)
    source_type: str = Field(..., description="e.g., official_guideline, position_stand")
    source_status: str = Field(..., description="e.g., active, superseded, historical")
    evidence_level: str = Field(..., description="e.g., high, moderate, low")
    retrieved_date: str = Field(..., description="Date added to the KB")
    section: str = Field(..., description="Section of the document the text comes from")
    page: str = Field(..., description="Page number or 'Webpage'")
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
    section: str
    page: str
    source_url: str
    source_status: str
    text_type: str
