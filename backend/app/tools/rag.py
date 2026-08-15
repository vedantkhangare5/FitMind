from typing import Optional
from app.rag.retrieval import RetrievalService

# Lazy initialization to avoid connecting to ChromaDB if the module is just imported
_retrieval_service: Optional[RetrievalService] = None

def get_retrieval_service() -> RetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service

def execute_search_knowledge(query: str, top_k: int = 5) -> dict:
    service = get_retrieval_service()
    
    # RetrievalService.search returns a list of RetrievalResult Pydantic models
    results = service.search(query=query, top_k=top_k)
    
    return {
        "results": [result.model_dump() for result in results]
    }
