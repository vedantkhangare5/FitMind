from typing import List
from app.rag.embeddings import EmbeddingService
from app.rag.vectorstore import VectorStore
from app.schemas.knowledge import RetrievalResult

class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def search(self, query: str, top_k: int = 5, filters: dict = None) -> List[RetrievalResult]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
            
        # 1. Generate query embedding
        query_embedding = self.embedding_service.embed_query(query)
        
        # 2. Search ChromaDB
        db_results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            where=filters
        )
        
        # 3. Structure results
        results = []
        if not db_results["ids"] or not db_results["ids"][0]:
            return results
            
        # ChromaDB returns lists of lists because it supports multiple queries at once.
        # We only sent one query, so we access index 0.
        ids = db_results["ids"][0]
        documents = db_results["documents"][0]
        metadatas = db_results["metadatas"][0]
        distances = db_results["distances"][0]
        
        for i in range(len(ids)):
            meta = metadatas[i]
            results.append(
                RetrievalResult(
                    chunk_id=ids[i],
                    document_id=meta.get("document_id", ""),
                    text=documents[i],
                    title=meta.get("title", ""),
                    source_name=meta.get("source_name", ""),
                    source_url=meta.get("source_url", ""),
                    source_status=meta.get("source_status", ""),
                    text_type=meta.get("text_type", ""),
                    topic=meta.get("topic", ""),
                    section=meta.get("section", ""),
                    page=str(meta.get("page", "")),
                    distance=distances[i]
                )
            )
            
        return results
