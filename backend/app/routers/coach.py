from fastapi import APIRouter, HTTPException, Depends
from app.schemas.agent import CoachRequest, CoachResponse
from app.agent.orchestrator import AgentOrchestrator
from app.auth import get_current_user

router = APIRouter(prefix="/api/coach", tags=["coach"])

@router.post("", response_model=CoachResponse)
def generate_coaching(request: CoachRequest, user_id: int = Depends(get_current_user)):
    try:
        orchestrator = AgentOrchestrator(mode="coach")
        return orchestrator.ask(request, user_id)
    except ValueError:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Coaching error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
