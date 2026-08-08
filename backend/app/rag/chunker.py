from typing import List
from app.schemas.knowledge import KnowledgeDocument, DocumentChunk

def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    A simple custom chunker that splits text deterministically by characters,
    respecting chunk_size and chunk_overlap.
    Avoids cutting words in half where possible.
    """
    if not text:
        return []

    words = text.split(" ")
    chunks = []
    current_chunk_words = []
    current_length = 0

    i = 0
    while i < len(words):
        word = words[i]
        # +1 for the space
        word_len = len(word) + (1 if current_length > 0 else 0)

        if current_length + word_len > chunk_size and current_length > 0:
            # Chunk is full, save it
            chunks.append(" ".join(current_chunk_words))
            
            # Step back to create overlap
            # We backtrack words until the overlapping length is approx chunk_overlap
            overlap_length = 0
            back_steps = 0
            for w in reversed(current_chunk_words):
                overlap_length += len(w) + 1
                back_steps += 1
                if overlap_length >= chunk_overlap:
                    break
                    
            # Set up the next chunk starting with the overlap
            # Ensure we always advance at least 1 word to avoid infinite loops
            # if a single word is larger than chunk_size
            if back_steps == len(current_chunk_words):
                back_steps = len(current_chunk_words) - 1
                
            i = i - back_steps
            current_chunk_words = []
            current_length = 0
        else:
            current_chunk_words.append(word)
            current_length += word_len
            i += 1

    if current_chunk_words:
        chunks.append(" ".join(current_chunk_words))

    return chunks

def chunk_document(doc: KnowledgeDocument, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[DocumentChunk]:
    """
    Takes a validated KnowledgeDocument and splits its text into DocumentChunk objects.
    Preserves critical metadata and assigns a deterministic chunk_id.
    """
    raw_chunks = split_text(doc.text, chunk_size, chunk_overlap)
    document_chunks = []
    
    for idx, text in enumerate(raw_chunks):
        # Deterministic ID combining document ID and its sequence position
        chunk_id = f"{doc.document_id}_chunk_{idx}"
        
        chunk = DocumentChunk(
            chunk_id=chunk_id,
            document_id=doc.document_id,
            text=text,
            chunk_index=idx,
            source_name=doc.source_name,
            title=doc.title,
            topic=doc.topic,
            section=doc.section,
            page=doc.page,
            source_url=doc.source_url,
            source_status=doc.source_status,
            text_type=doc.text_type
        )
        document_chunks.append(chunk)
        
    return document_chunks
