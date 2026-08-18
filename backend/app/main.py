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

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import fitness, rag, agent, profile, progress, coach, behavior, auth

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: initialize resources on startup, clean up on shutdown."""
    # Startup: create SQLite tables
    init_db()
    logger.info("Application startup complete.")
    yield
    # Shutdown: nothing to clean up for now
    logger.info("Application shutdown complete.")

# Create the FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Evidence-based fitness and nutrition intelligence agent for Indian users",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

# Include routers
app.include_router(auth.router)
app.include_router(fitness.router)
app.include_router(rag.router)
app.include_router(agent.router, prefix="/api")
app.include_router(profile.router)
app.include_router(progress.router)
app.include_router(coach.router)
app.include_router(behavior.router)

