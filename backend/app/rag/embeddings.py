import os
from typing import List
from google import genai
from google.genai.errors import APIError

class EmbeddingService:
    """
    Abstraction for the embedding provider.
    Currently uses Google Gemini 'gemini-embedding-2' via google-genai SDK.
    """
    def __init__(self):
        # We enforce API key loading from env vars to avoid hardcoding secrets.
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
            
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-embedding-2"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embeds a list of document chunks.
        Fails loudly if the API errors (e.g., quota or auth).
        """
        if not texts:
            return []
            
        try:
            # We pass the batch of texts to the embedding model
            response = self.client.models.embed_content(
                model=self.model,
                contents=texts
            )
            # The response.embeddings is a list of Embedding objects
            # which have a `values` property containing the float list.
            return [e.values for e in response.embeddings]
        except APIError as e:
            raise RuntimeError(f"Gemini Embedding API failed: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected embedding error: {str(e)}")
