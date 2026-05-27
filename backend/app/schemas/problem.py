"""Pydantic schemas for problem-related API responses."""

from typing import List, Dict, Any, Optional

from pydantic import BaseModel


class TestCase(BaseModel):
    """A single test case."""
    input: str = ""
    expected_output: str = ""


class ProblemResponse(BaseModel):
    """Problem returned to the frontend (visible test cases only)."""
    title: str
    description: str
    starter_code: str
    test_cases: List[TestCase] = []
    concept_id: str
    difficulty: int


class SubmissionRequest(BaseModel):
    """Request body for submitting code."""
    source_code: str


class TestResult(BaseModel):
    """Result for a single test case."""
    test_index: int
    input: str
    expected: str
    actual: str
    status: str
    is_hidden: bool = False


class SubmissionResponse(BaseModel):
    """Response after submitting code."""
    outcome: str  # "pass" or "fail"
    message: Optional[str] = None
    hint: Optional[str] = None
    results: List[TestResult] = []
    attempts_on_concept: Optional[int] = None
