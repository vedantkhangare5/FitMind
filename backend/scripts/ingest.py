import os
import json
import glob
from pydantic import ValidationError
from dotenv import load_dotenv

# Load env variables (for GEMINI_API_KEY)
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.local"))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Import our custom RAG modules
from app.schemas.knowledge import KnowledgeDocument
from app.rag.chunker import chunk_document
from app.rag.embeddings import EmbeddingService
from app.rag.vectorstore import VectorStore

def load_documents(knowledge_dir: str) -> list[KnowledgeDocument]:
    """Finds and validates all JSON files in the raw directories."""
    raw_dir = os.path.join(knowledge_dir, "raw")
    search_pattern = os.path.join(raw_dir, "**", "*.json")
    
    docs = []
    # Recursive search for all JSONs
    for filepath in glob.glob(search_pattern, recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # Validation occurs here via Pydantic
                doc = KnowledgeDocument(**data)
                docs.append(doc)
            except json.JSONDecodeError:
                print(f"Error: {filepath} is not valid JSON.")
                raise
            except ValidationError as e:
                print(f"Error: {filepath} failed schema validation.")
                print(e)
                raise
                
    return docs

def main():
    print("Starting Knowledge Ingestion Pipeline...")
    
    # 1. Setup paths
    backend_dir = os.path.dirname(os.path.dirname(__file__))
    project_root = os.path.dirname(backend_dir)
    knowledge_dir = os.path.join(project_root, "knowledge")
    
    # 2. Load and validate
    docs = load_documents(knowledge_dir)
    print(f"Documents discovered & valid: {len(docs)}")
    
    if not docs:
        print("No documents found. Exiting.")
        return
        
    # 3. Chunking
    all_chunks = []
    for doc in docs:
        chunks = chunk_document(doc, chunk_size=1000, chunk_overlap=200)
        all_chunks.extend(chunks)
        
    print(f"Chunks generated: {len(all_chunks)}")
    
    # 4. Embeddings
    print("Initializing EmbeddingService (gemini-embedding-2)...")
    try:
        embedding_service = EmbeddingService()
    except ValueError as e:
        print(f"FAILED: {e}")
        return
        
    print("Generating embeddings... (this may take a moment)")
    texts_to_embed = [c.text for c in all_chunks]
    try:
        embeddings = embedding_service.embed_documents(texts_to_embed)
    except RuntimeError as e:
        print(f"FAILED to generate embeddings: {e}")
        return
        
    print(f"Embeddings generated: {len(embeddings)}")
    
    # 5. Store in ChromaDB
    print("Initializing VectorStore...")
    vector_store = VectorStore()
    
    print("Upserting chunks to ChromaDB...")
    vector_store.upsert_chunks(all_chunks, embeddings)
    
    # 6. Report
    print("--------------------------------------------------")
    print(f"Documents loaded:       {len(docs)}")
    print(f"Chunks created:         {len(all_chunks)}")
    print(f"Embeddings generated:   {len(embeddings)}")
    print(f"Total Records in DB:    {vector_store.count()}")
    print("Errors:                 0")
    print("--------------------------------------------------")
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
