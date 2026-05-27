"""
Session Routes — Start sessions, submit code, get details.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.session import Session
from app.routers.auth import get_current_user
from app.schemas.problem import SubmissionRequest
from app.schemas.session import SessionStartResponse, SessionDetailResponse
from app.services.adaptive_loop import AdaptiveLoopService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/session", tags=["session"])


def get_adaptive_loop(request: Request) -> AdaptiveLoopService:
    """Get the AdaptiveLoopService from app state."""
    return request.app.state.adaptive_loop


@router.post("/start", response_model=SessionStartResponse)
async def start_session(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new tutoring session. The AI generates a problem tailored to the student."""
    loop_service = get_adaptive_loop(request)

    try:
        # Check if backtracking is needed
        # Look at the last session to see if we should backtrack
        last_session_result = await db.execute(
            select(Session)
            .where(Session.user_id == current_user.id)
            .order_by(Session.created_at.desc())
            .limit(1)
        )
        last_session = last_session_result.scalar_one_or_none()

        force_concept = None
        if last_session and last_session.outcome == "fail":
            backtrack = await loop_service.check_backtrack(
                current_user.id, last_session.concept_id, db
            )
            if backtrack:
                force_concept = backtrack
                logger.info(
                    f"Backtracking user {current_user.id} from "
                    f"{last_session.concept_id} to {backtrack}"
                )

        result = await loop_service.start_session(
            current_user.id, db, force_concept=force_concept
        )
        return SessionStartResponse(**result)

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start session")


@router.post("/{session_id}/submit")
async def submit_code(
    session_id: int,
    body: SubmissionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit code for a session. Returns test results and optional Socratic hint."""
    loop_service = get_adaptive_loop(request)

    try:
        result = await loop_service.submit_code(
            session_id=session_id,
            source_code=body.source_code,
            user_id=current_user.id,
            db=db,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Submission failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Submission processing failed")


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific session."""
    result = await db.execute(
        select(Session).where(
            Session.id == session_id,
            Session.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionDetailResponse.model_validate(session)


@router.post("/{session_id}/next", response_model=SessionStartResponse)
async def next_problem(
    session_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """After completing a problem, start a new session with the next problem."""
    loop_service = get_adaptive_loop(request)

    try:
        result = await loop_service.start_session(current_user.id, db)
        return SessionStartResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start next session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate next problem")
