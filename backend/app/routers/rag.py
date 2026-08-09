from fastapi import APIRouter, HTTPException, Depends
from app.schemas.knowledge import SearchRequest, SearchResponse
from app.schemas.rag import GenerateRequest, GenerateResponse
from app.rag.retrieval import RetrievalService
from app.rag.generation import GenerationService, INSUFFICIENT_CONTEXT_MESSAGE

router = APIRouter(prefix="/api/rag", tags=["rag"])

def get_retrieval_service():
    return RetrievalService()

def get_generation_service():
    return GenerationService()

@router.post("/search", response_model=SearchResponse)
def search_knowledge(request: SearchRequest, service: RetrievalService = Depends(get_retrieval_service)):
    """
    Searches the knowledge base for the most relevant chunks.
    """
    filters = {}
    if request.topic:
        filters["topic"] = request.topic
    if request.source_status:
        filters["source_status"] = request.source_status
        
    where = None
    if filters:
        if len(filters) == 1:
            where = filters
        else:
            where = {"$and": [{k: v} for k, v in filters.items()]}
            
    try:
        results = service.search(
            query=request.query,
            top_k=request.top_k,
            filters=where
        )
        return SearchResponse(query=request.query, results=results)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/ask", response_model=GenerateResponse)
def ask_knowledge(
    request: GenerateRequest, 
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    generation_service: GenerationService = Depends(get_generation_service)
):
    """
    Full Grounded RAG Pipeline: Retrieves chunks and generates an answer.
    """
    try:
        # 1. Retrieval
        retrieved_results = retrieval_service.search(
            query=request.query,
            top_k=request.top_k,
            filters=None
        )
        
        # 2. Sufficiency Check (Pre-generation)
        if not retrieved_results:
            return GenerateResponse(
                answer=INSUFFICIENT_CONTEXT_MESSAGE,
                citations=[],
                grounded=False,
                insufficient_context=True
            )
            
        best_distance = min(res.distance for res in retrieved_results)
        # If the best result is still worse than the threshold, we reject immediately
        # (lower distance is better for Squared L2)
        if request.distance_threshold is not None and best_distance > request.distance_threshold:
            return GenerateResponse(
                answer=INSUFFICIENT_CONTEXT_MESSAGE,
                citations=[],
                grounded=False,
                insufficient_context=True
            )
            
        # 3. Generation
        generate_response = generation_service.generate_grounded_answer(
            query=request.query,
            retrieved_results=retrieved_results
        )
        
        return generate_response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
