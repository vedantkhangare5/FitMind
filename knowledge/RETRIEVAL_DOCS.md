# Phase 3C: Retrieval Engine Documentation

This document explains how the Retrieval Engine functions in FitMind AI.

## Query Embeddings

When a user submits a natural language search query, the `RetrievalService` invokes `EmbeddingService.embed_query(query)`. This passes the text to the `gemini-embedding-2` model, creating a 768-dimensional vector representation of the query's semantic meaning.

## ChromaDB Similarity Search

The query embedding is passed to `VectorStore.search()`, which executes a similarity search against the persistent ChromaDB collection. ChromaDB calculates the mathematical distance between the query vector and all document chunk vectors. The current implementation uses **Squared L2 distance**.

## Top-K Retrieval

The parameter `top_k` specifies the maximum number of results to return. ChromaDB ranks the chunks by distance (lower distance = more similar) and returns the most similar `top_k` chunks.

## Metadata Filtering

Queries can optionally be filtered by metadata attached to chunks during ingestion. For instance, `filters={"topic": "Sleep"}` restricts the search strictly to chunks containing that metadata attribute.

## Limitations

- **No Reranking**: The retrieval relies entirely on the raw embedding distance.
- **Lexical Gap**: Pure vector search may struggle with exact keyword matches (e.g. specific IDs).
- **Hard Top-K**: Fixed cutoff size regardless of absolute distance values.

## Initial Evaluation Results

We established a 10-question evaluation dataset derived strictly from our 5 knowledge base documents. The CLI (`retrieval_cli.py --eval`) tests this automatically, checking Top-1 and Top-3 accuracy to ensure baseline semantic retrieval works before adding LLMs.
