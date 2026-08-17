from fastapi import APIRouter, HTTPException
from app.schemas.agent import CoachRequest, CoachResponse
from app.agent.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/api/coach", tags=["coach"])

@router.post("", response_model=CoachResponse)
def generate_coaching(request: CoachRequest):
    try:
        orchestrator = AgentOrchestrator(mode="coach")
        return orchestrator.ask(request)
    except ValueError:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Coaching error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
