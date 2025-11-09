"""
Main FastAPI application for Dream Job Ally Deduction.

This module initializes the FastAPI app, configures middleware, and includes all API routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.api.middleware.auth_middleware import AuthenticationMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Dream Job Ally Deduction API",
    description="API for analyzing resumes and dream jobs to deduce professional ally types",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(AuthenticationMiddleware)


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "dream-job-ally-deduction"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Dream Job Ally Deduction API",
        "version": "0.1.0",
        "docs": "/api/docs",
    }


# Include routers
from src.api.routes import resume, dream_job, ally_types, auth

app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(resume.router, prefix="/api/v1", tags=["resume"])
app.include_router(dream_job.router, prefix="/api/v1", tags=["dream-job"])
app.include_router(ally_types.router, prefix="/api/v1", tags=["ally-types"])
# app.include_router(discovery.router, prefix="/api/v1", tags=["discovery"])  # US2 - not implemented yet


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
