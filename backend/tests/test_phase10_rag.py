import pytest
import os
from unittest.mock import patch, MagicMock
from app.rag.retrieval import RetrievalService
from app.schemas.knowledge import RetrievalResult

@patch("app.rag.retrieval.EmbeddingService")
@patch("app.rag.retrieval.VectorStore")
def test_retrieval_service_filters_test_only(mock_vs_class, mock_emb_class):
    mock_emb = MagicMock()
    mock_emb.embed_query.return_value = [0.1, 0.2]
    mock_emb_class.return_value = mock_emb
    
    mock_vs = MagicMock()
    # Mocking that search is called, we want to assert the `where` clause
    mock_vs.search.return_value = {
        "ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]
    }
    mock_vs_class.return_value = mock_vs
    
    from app.tools.rag import execute_search_knowledge
    
    # We must patch the get_retrieval_service to return our mock
    service = RetrievalService()
    
    with patch("app.tools.rag.get_retrieval_service", return_value=service):
        execute_search_knowledge("test query")
        
        # Verify the filter was passed to VectorStore
        mock_vs.search.assert_called_once_with(
            query_embedding=[0.1, 0.2], 
            top_k=5, 
            where={"source_status": {"$ne": "test_only"}}
        )

def test_citation_validation_strips_hallucinations():
    from app.agent.orchestrator import AgentOrchestrator
    from app.schemas.agent import AgentRequest
    from google.genai.errors import APIError
    
    agent = AgentOrchestrator(profile_repo=MagicMock())
    
    with patch.object(agent.client.models, 'generate_content') as mock_gen:
        # Turn 1: tool call
        class MockCall:
            def __init__(self, name, args):
                self.name = name
                self.args = args
                
        mock_resp1 = MagicMock()
        mock_resp1.function_calls = [MockCall(name="search_knowledge", args={"query": "test"})]
        mock_resp1.text = ""
        
        # Turn 2: final answer with hallucinated citations
        mock_resp2 = MagicMock()
        mock_resp2.function_calls = []
        mock_resp2.text = '{"answer": "Here is the info.", "citations": ["doc_real", "doc_fake"], "grounded": true, "insufficient_context": false}'
        
        mock_gen.side_effect = [mock_resp1, mock_resp2]
        
        # We need to mock the registry to return a real doc
        with patch("app.agent.orchestrator.registry.execute") as mock_exec:
            mock_exec.return_value = {
                "success": True, 
                "data": {
                    "results": [{"document_id": "doc_real", "title": "Real Doc", "source_name": "Source", "source_url": "Url", "section": "1", "page": "1", "text_type": "summary", "distance": 0.1, "chunk_id": "c1", "text": "mock text", "source_status": "production", "topic": "test topic"}]
                }
            }
            
            res = agent.ask(AgentRequest(query="test"), user_id=1)
            
            assert res.generation_error is False
            assert res.grounded is True
            assert len(res.citations) == 1
            assert res.citations[0].document_id == "doc_real"
