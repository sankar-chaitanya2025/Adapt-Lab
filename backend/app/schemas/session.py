"""Pydantic schemas for session-related API responses."""

from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel


class SessionStartResponse(BaseModel):
    """Response when starting a new tutoring session."""
    session_id: int
    problem: Dict[str, Any]


class SessionDetailResponse(BaseModel):
    """Detailed session information."""
    id: int
    user_id: int
    concept_id: str
    difficulty_level: int
    problem_json: Dict[str, Any]
    submitted_code: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    socratic_hints: Optional[List[str]] = None
    outcome: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProgressSummary(BaseModel):
    """Summary of student progress across all concepts."""
    total_concepts: int
    mastered: int
    in_progress: int
    struggling: int
    not_started: int


class ConceptProgress(BaseModel):
    """Progress for a single concept."""
    id: str
    title: str
    level: int
    mastery_level: int = 0
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    current_difficulty: int = 1
    status: str = "not_started"
    last_attempted: Optional[str] = None


class ProgressResponse(BaseModel):
    """Full progress response."""
    summary: ProgressSummary
    concepts: List[ConceptProgress]
    capability_matrix: Dict[str, Any]


class GraphNode(BaseModel):
    """A node in the knowledge graph with mastery overlay."""
    id: str
    title: str
    level: int
    prerequisites: List[str] = []
    unlocks: List[str] = []
    mastery_level: int = 0
    status: str = "not_started"


class GraphResponse(BaseModel):
    """Knowledge graph with mastery overlay."""
    nodes: List[GraphNode]


class SubmissionHistoryItem(BaseModel):
    """A single item in the submission history."""
    id: int
    concept_id: str
    difficulty_level: int
    outcome: Optional[str] = None
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SubmissionHistoryResponse(BaseModel):
    """Paginated submission history."""
    items: List[SubmissionHistoryItem]
    total: int
    page: int
    per_page: int
