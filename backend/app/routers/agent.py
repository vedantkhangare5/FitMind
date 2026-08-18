from fastapi import APIRouter, HTTPException, Depends
from app.schemas.agent import AgentRequest, AgentResponse
from app.agent.orchestrator import AgentOrchestrator
from app.auth import get_current_user

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/ask", response_model=AgentResponse)
def ask_agent(request: AgentRequest, user_id: int = Depends(get_current_user)):
    try:
        orchestrator = AgentOrchestrator()
        return orchestrator.ask(request, user_id)
    except ValueError:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
