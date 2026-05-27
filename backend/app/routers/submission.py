"""
Submission Routes — Submission history.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.session import Session
from app.routers.auth import get_current_user
from app.schemas.session import SubmissionHistoryItem, SubmissionHistoryResponse

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.get("/history", response_model=SubmissionHistoryResponse)
async def get_submission_history(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated list of past sessions for the authenticated user."""
    # Count total
    count_result = await db.execute(
        select(func.count(Session.id)).where(Session.user_id == current_user.id)
    )
    total = count_result.scalar() or 0

    # Fetch page
    offset = (page - 1) * per_page
    result = await db.execute(
        select(Session)
        .where(Session.user_id == current_user.id)
        .order_by(Session.created_at.desc())
        .offset(offset)
        .limit(per_page)
    )
    sessions = result.scalars().all()

    items = [
        SubmissionHistoryItem.model_validate(s)
        for s in sessions
    ]

    return SubmissionHistoryResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
    )
