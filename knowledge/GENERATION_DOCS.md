# Phase 3D: Generation & Grounding Documentation

This document explains the Grounded Generation mechanics implemented in FitMind AI.

## Flow
User Query → Query Embedding → ChromaDB (Vector Search) → **Sufficiency Check** → Gemini Prompt → Structured JSON → Citation Validation → API Response

## Grounding Strategy

The grounding strategy ensures that the generated response relies solely on the retrieved evidence:
- **Prompt Isolation:** Retrieved evidence chunks are placed into isolated, numbered blocks to prevent prompt injection and distinguish them from instructions.
- **Explicit Fallback:** The LLM is explicitly instructed to refuse to answer if the context is insufficient, and output a strict `insufficient_context: true` flag.
- **No LLM Fallback:** The backend leverages this structured output to forcefully intercept the response and return a deterministic, safe refusal rather than risking hallucinatory leakage from pretrained weights.

## Retrieval Sufficiency Check

Before calling Gemini, the `RetrievalService` distances are checked against a `distance_threshold` parameter (default `1.5` for Squared L2 distance). If all retrieved chunks have a distance exceeding this threshold, the backend immediately halts the generation process and returns an insufficient context response. This avoids wasting LLM tokens on completely irrelevant contexts.

## Citation Validation

LLMs are prone to hallucinating metadata such as URLs and page numbers. We avoid this by:
1. Providing the deterministic `document_id` to the LLM.
2. Requiring the LLM to output a list of the exact IDs it used as citations.
3. The backend strictly validating this list against the original retrieved chunks.
4. If an ID is hallucinated (unknown/fake), it is discarded. If no valid citations remain but the LLM claims to be grounded, the response is downgraded to an insufficient-context refusal.
5. Legitimate citations are enriched with authentic database metadata (titles, URLs, page numbers) to construct the final payload.
