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
from app.database import init_db, get_connection
from app.routers import fitness, rag, agent, profile, progress, coach, behavior, auth

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
import traceback

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

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")
    if settings.APP_ENV == "production":
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "trace": traceback.format_exc()}
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    db_status = "healthy"
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception as e:
        db_status = f"unhealthy: {e}"
        
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
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

