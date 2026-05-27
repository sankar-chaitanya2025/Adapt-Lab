"""
AdaptLab — FastAPI Application Entry Point.

Configures the application with:
- Lifespan context manager (loads knowledge graph, creates adaptive loop service)
- CORS middleware
- All API routers
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.engine.knowledge_graph import KnowledgeGraph
from app.services.adaptive_loop import AdaptiveLoopService
from app.routers import auth, session, progress, submission

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: startup and shutdown events.

    On startup:
    - Load the knowledge graph from the curriculum directory
    - Initialize the adaptive loop service
    """
    logger.info("=" * 60)
    logger.info("  AdaptLab — Starting up...")
    logger.info("=" * 60)

    # Load knowledge graph
    try:
        kg = KnowledgeGraph(settings.CURRICULUM_PATH)
        app.state.knowledge_graph = kg
        logger.info(f"Knowledge graph loaded: {len(kg.get_all_concept_ids())} concepts")
    except Exception as e:
        logger.error(f"FATAL: Failed to load knowledge graph: {e}")
        raise

    # Initialize adaptive loop service
    app.state.adaptive_loop = AdaptiveLoopService(kg)
    logger.info("Adaptive loop service initialized")

    logger.info("=" * 60)
    logger.info("  AdaptLab — Ready!")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("AdaptLab shutting down...")


# Create FastAPI app
app = FastAPI(
    title="AdaptLab",
    description="Multi-agent Socratic AI tutor for adaptive C programming education",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(session.router)
app.include_router(progress.router)
app.include_router(submission.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "adaptlab"}
