import os
from typing import List
from google import genai
from google.genai.errors import APIError
from app.config import settings

class EmbeddingService:
    """
    Abstraction for the embedding provider.
    Currently uses Google Gemini 'gemini-embedding-2' via google-genai SDK.
    """
    def __init__(self):
        # We enforce API key loading from settings to avoid hardcoding secrets.
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key or self.api_key == "not-set-yet":
            raise ValueError("GEMINI_API_KEY is not configured properly.")
            
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-embedding-2"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of document chunks.
        Fails loudly if the API errors (e.g., quota or auth).
        """
        if not texts:
            return []
            
        embeddings = []
        try:
            for text in texts:
                response = self.client.models.embed_content(
                    model=self.model,
                    contents=text
                )
                if response.embeddings and response.embeddings[0].values:
                    embeddings.append(response.embeddings[0].values)
        except APIError as e:
            raise RuntimeError(f"Gemini Embedding API failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected embedding error: {str(e)}")
            
        if len(embeddings) != len(texts):
            raise RuntimeError(
                f"Embedding count mismatch. Expected {len(texts)} embeddings, "
                f"but generated {len(embeddings)}."
            )
            
        return embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Embeds a single natural-language query.
        Returns a single vector.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
            
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=query.strip()
            )
            if response.embeddings and response.embeddings[0].values:
                return response.embeddings[0].values
            else:
                raise RuntimeError("No embedding returned for query.")
        except APIError as e:
            raise RuntimeError(f"Gemini Embedding API failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected embedding error: {str(e)}")
