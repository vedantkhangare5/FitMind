# FitMind AI Knowledge Base

This directory contains the foundational, deterministic knowledge for FitMind AI's Retrieval-Augmented Generation (RAG) system.

## Source Quality Rules
To ensure the LLM generates safe and accurate answers, we ONLY include sources that meet these criteria:
1. **Government Health Organizations:** WHO, NIH, NIDDK, CDC.
2. **Professional Organizations:** ACSM, NSCA, ISSN.
3. **Peer-Reviewed Research:** Published in reputable journals (e.g., PubMed indexed).
4. **Official Position Stands:** Official consensus statements.

**What DOES NOT belong:**
- Influencer blogs or videos
- Reddit posts or anecdotal evidence
- AI-generated summaries (unless clearly delineated as `editorial_summary`)
- SEO-driven articles (Healthline, WebMD, etc., unless directly citing primary sources, in which case we fetch the primary source)

## Metadata Requirements
All knowledge documents must be in JSON format and strictly follow the `templates/knowledge_document.json` schema.

Key rules for data provenance:
- **`text_type`**: Must be either `"source_excerpt"` for direct, unedited quotes, or `"editorial_summary"` for our condensed notes. DO NOT mix them or fabricate quotes.
- **`source_status`**: e.g., `"active"`, `"superseded"`, `"historical"`, `"under_review"`.
- **`section` & `page`**: Provide exact provenance for excerpts whenever available.

## How to add new sources
1. Identify a valid source meeting the quality rules.
2. Add it to `sources/source_registry.json`.
3. Copy `templates/knowledge_document.json` into the appropriate `raw/` subdirectory (`nutrition`, `training`, etc.).
4. Fill out the JSON, strictly separating excerpts from summaries.

## Ingestion Pipeline & Architecture
Once JSON documents are added, run the ingestion script from the backend:
```bash
python scripts/ingest.py
```

### 1. Custom Chunking
We employ a custom Python text chunker (default ~1000 characters, ~200 character overlap). Chunking prevents large documents from diluting context during RAG searches and fits the text within embedding limits. Overlaps ensure concepts spanning chunk boundaries are preserved.

### 2. Embeddings
We use the `gemini-embedding-2` model via the `google-genai` SDK to convert chunk text into vector embeddings. (Requires `GEMINI_API_KEY` in `.env.local`).

### 3. ChromaDB & Idempotency
Embeddings, text, and metadata are persisted locally in `backend/chroma_db`. 
Every chunk is assigned a deterministic ID (`{document_id}_chunk_{index}`). Because of this, the `ingest.py` script is fully idempotent. Re-running it will update existing chunks with identical IDs, safely preventing duplicate records in the vector store.
