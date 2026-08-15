from fastapi import APIRouter
from app.schemas.agent import AgentRequest, AgentResponse
from app.agent.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/ask", response_model=AgentResponse)
def ask_agent(request: AgentRequest):
    orchestrator = AgentOrchestrator()
    return orchestrator.ask(request)
