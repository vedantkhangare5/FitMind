from fastapi import APIRouter, HTTPException
from app.schemas.agent import AgentRequest, AgentResponse
from app.agent.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/ask", response_model=AgentResponse)
def ask_agent(request: AgentRequest):
    try:
        orchestrator = AgentOrchestrator()
        return orchestrator.ask(request)
    except ValueError:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
