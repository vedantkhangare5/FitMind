"""
FastAPI application entry point.

This is the file that uvicorn runs to start the server:
    uvicorn app.main:app --reload

It creates the FastAPI application, configures CORS (Cross-Origin Resource
Sharing), and defines the health-check endpoint.

WHAT IS CORS?
When your frontend (localhost:3000) tries to call your backend (localhost:8000),
the browser blocks it by default for security reasons — they're on different
"origins" (different ports count as different origins). CORS tells the browser
"it's okay, allow requests from this specific frontend."

Without CORS configured, the frontend would get an error like:
"Access to fetch at 'http://localhost:8000' has been blocked by CORS policy"

WHY THIS FILE EXISTS:
- This is the single entry point for the entire backend
- If removed, there is no backend — uvicorn has nothing to run
"""

from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import fitness, rag, agent

# Create the FastAPI application
# The title and version appear in the auto-generated docs at /docs
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Evidence-based fitness and nutrition intelligence agent for Indian users",
)

# Configure CORS — allow the frontend to call this backend
# In development, the frontend runs on localhost:3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js dev server
        "http://127.0.0.1:3000",  # Same thing, different notation
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.get("/api/health")
def health_check():
    """
    Health check endpoint.

    Returns the current status of the backend server.
    This is the simplest possible endpoint — it just confirms
    the server is running and can respond to requests.

    Used by:
    - The frontend to check if the backend is reachable
    - Monitoring tools to verify the server is alive
    - Deployment platforms to know the app started successfully
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# Include routers
app.include_router(fitness.router)
app.include_router(rag.router)
app.include_router(agent.router, prefix="/api")
