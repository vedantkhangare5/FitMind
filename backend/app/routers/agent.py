from fastapi import APIRouter, HTTPException
from app.schemas.agent import AgentRequest, AgentResponse
from app.agent.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/ask", response_model=AgentResponse)
def ask_agent(request: AgentRequest):
    try:
        orchestrator = AgentOrchestrator()
        return orchestrator.ask(request)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
