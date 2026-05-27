"""
Progress Routes — Capability matrix, progress summary, knowledge graph.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.routers.auth import get_current_user
from app.services.capability import get_progress_summary
from app.schemas.session import (
    ProgressResponse,
    ProgressSummary,
    ConceptProgress,
    GraphResponse,
    GraphNode,
)

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("", response_model=ProgressResponse)
async def get_progress(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the student's full progress: summary, per-concept details, and raw matrix."""
    kg = request.app.state.knowledge_graph
    cap_matrix = current_user.capability_matrix or {}

    summary_data = get_progress_summary(cap_matrix)
    summary = ProgressSummary(**summary_data)

    concepts = []
    for concept in kg.get_all_concepts():
        cid = concept["id"]
        cap = cap_matrix.get(cid, {})
        concepts.append(ConceptProgress(
            id=cid,
            title=concept["title"],
            level=concept["level"],
            mastery_level=cap.get("mastery_level", 0),
            attempts=cap.get("attempts", 0),
            successes=cap.get("successes", 0),
            failures=cap.get("failures", 0),
            current_difficulty=cap.get("current_difficulty", 1),
            status=cap.get("status", "not_started"),
            last_attempted=cap.get("last_attempted"),
        ))

    return ProgressResponse(
        summary=summary,
        concepts=concepts,
        capability_matrix=cap_matrix,
    )


@router.get("/graph", response_model=GraphResponse)
async def get_progress_graph(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the knowledge graph structure with mastery overlay."""
    kg = request.app.state.knowledge_graph
    cap_matrix = current_user.capability_matrix or {}

    nodes = []
    for concept in kg.get_all_concepts():
        cid = concept["id"]
        cap = cap_matrix.get(cid, {})
        nodes.append(GraphNode(
            id=cid,
            title=concept["title"],
            level=concept["level"],
            prerequisites=kg.get_prerequisites(cid),
            unlocks=kg.get_unlocks(cid),
            mastery_level=cap.get("mastery_level", 0),
            status=cap.get("status", "not_started"),
        ))

    return GraphResponse(nodes=nodes)
