import os
from typing import List
import chromadb
from chromadb.config import Settings
from app.schemas.knowledge import DocumentChunk

class VectorStore:
    """
    Manages the persistent local ChromaDB instance and collections.
    """
    def __init__(self, persist_directory: str = "chroma_db", collection_name: str = "fitmind_knowledge"):
        # We ensure it creates a persistent DB in the backend dir
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.persist_directory = os.path.join(backend_dir, persist_directory)
        
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create the collection
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def upsert_chunks(self, chunks: List[DocumentChunk], embeddings: List[List[float]]):
        """
        Upserts (inserts or updates) chunks into ChromaDB.
        Idempotency: Since chunk_ids are deterministic, running this twice
        on the same documents simply overwrites the records without duplicating.
        """
        if not chunks:
            return

        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            ids.append(chunk.chunk_id)
            documents.append(chunk.text)
            
            # ChromaDB metadatas cannot contain None or complex types
            # so we ensure they are all strings or ints, and remove None values.
            raw_meta = {
                "document_id": chunk.document_id,
                "source_name": chunk.source_name,
                "title": chunk.title,
                "topic": chunk.topic,
                "section": chunk.section,
                "page": chunk.page,
                "source_url": chunk.source_url,
                "source_status": chunk.source_status,
                "text_type": chunk.text_type,
                "chunk_index": chunk.chunk_index
            }
            # Remove keys where value is None
            safe_meta = {k: v for k, v in raw_meta.items() if v is not None}
            metadatas.append(safe_meta)

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, query_embedding: List[float], top_k: int = 5, where: dict = None) -> dict:
        """
        Searches ChromaDB for the most similar chunks.
        Returns the raw ChromaDB results dictionary.
        """
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

    def count(self) -> int:
        return self.collection.count()
