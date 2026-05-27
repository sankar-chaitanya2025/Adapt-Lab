"""
Adaptive Loop Service — Central Orchestrator.

Coordinates the entire tutoring flow:
  Teacher Agent → Generator Agent → Code Execution → Socratic Agent
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.session import Session
from app.agents.teacher import TeacherAgent
from app.agents.generator import GeneratorAgent
from app.agents.socratic import SocraticAgent
from app.engine.executor import CodeExecutor, ExecutorError
from app.services.capability import (
    update_capability_on_success,
    update_capability_on_failure,
)
from app.config import settings

logger = logging.getLogger(__name__)


class AdaptiveLoopService:
    """
    Orchestrates the adaptive tutoring loop:
    1. Teacher decides next topic
    2. Generator creates a problem
    3. Student submits code
    4. Code is executed in sandbox
    5. Socratic Agent provides guidance on failure
    6. Capability matrix is updated
    """

    def __init__(self, knowledge_graph):
        self.knowledge_graph = knowledge_graph
        self.teacher = TeacherAgent()
        self.generator = GeneratorAgent()
        self.socratic = SocraticAgent()
        self.executor = CodeExecutor(judge0_url=settings.JUDGE0_URL)

    async def start_session(
        self,
        user_id: int,
        db: AsyncSession,
        force_concept: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initialize a new tutoring session.

        1. Fetch user + capability matrix
        2. Teacher Agent decides next topic
        3. Generator Agent creates problem
        4. Save session to DB
        5. Return problem to frontend

        Args:
            user_id: The authenticated user's ID.
            db: Async database session.
            force_concept: Optional concept_id to force (for backtracking).

        Returns:
            Dict with session_id and problem details.
        """
        # 1. Fetch user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError(f"User {user_id} not found")

        capability_matrix = user.capability_matrix or {}
        kg_summary = self.knowledge_graph.get_graph_summary()

        # 2. Teacher decides next topic
        try:
            if force_concept:
                # Override with forced concept for backtracking
                cap = capability_matrix.get(force_concept, {})
                teacher_directive = {
                    "TARGET_TOPIC": force_concept,
                    "TARGET_LEVEL": max(cap.get("current_difficulty", 1), 1),
                    "FOCUS_AREA": "Review fundamentals and address knowledge gaps",
                    "REASONING": f"Backtracking to prerequisite '{force_concept}' due to struggling on dependent concept.",
                }
            else:
                teacher_directive = await self.teacher.decide_next(
                    capability_matrix, kg_summary
                )
        except Exception as e:
            logger.error(f"Teacher Agent failed: {e}")
            raise RuntimeError(
                "The AI tutor is temporarily unavailable. Please try again in a moment."
            )

        # 3. Generator creates problem
        try:
            problem = await self.generator.generate(teacher_directive)
        except Exception as e:
            logger.error(f"Generator Agent failed: {e}")
            raise RuntimeError(
                "Problem generation failed. Please try again."
            )

        # 4. Save session to DB
        session = Session(
            user_id=user_id,
            concept_id=teacher_directive["TARGET_TOPIC"],
            difficulty_level=teacher_directive["TARGET_LEVEL"],
            problem_json=problem,
            teacher_directive=teacher_directive,
            socratic_hints=[],
        )
        db.add(session)
        await db.flush()
        await db.refresh(session)

        # 5. Return problem (visible test cases only)
        visible_tests = problem.get("test_cases", {}).get("visible", [])
        return {
            "session_id": session.id,
            "problem": {
                "title": problem.get("title", ""),
                "description": problem.get("description", ""),
                "starter_code": problem.get("starter_code", ""),
                "test_cases": visible_tests,
                "concept_id": problem.get("concept_id", ""),
                "difficulty": problem.get("difficulty", 1),
            },
        }

    async def submit_code(
        self,
        session_id: int,
        source_code: str,
        user_id: int,
        db: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Handle a code submission.

        1. Fetch session
        2. Run all tests in Judge0
        3. Update capability matrix based on result
        4. Generate Socratic hint on failure
        5. Return results

        Args:
            session_id: The session to submit code for.
            source_code: The student's C source code.
            user_id: The authenticated user's ID.
            db: Async database session.

        Returns:
            Dict with outcome, results, and optional hint.
        """
        # 1. Fetch session
        result = await db.execute(
            select(Session).where(
                Session.id == session_id,
                Session.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError("Session not found")

        # Fetch user
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        # 2. Build test cases list
        problem = session.problem_json
        tc = problem.get("test_cases", {})
        all_tests = []
        for t in tc.get("visible", []):
            all_tests.append({**t, "is_hidden": False})
        for t in tc.get("hidden", []):
            all_tests.append({**t, "is_hidden": True})

        # 3. Execute in sandbox
        try:
            exec_result = await self.executor.run_all_tests(source_code, all_tests)
        except ExecutorError as e:
            session.submitted_code = source_code
            session.outcome = "error"
            session.execution_result = {"error": str(e)}
            await db.flush()
            return {
                "outcome": "error",
                "message": str(e),
                "results": [],
            }

        # Store submission data
        session.submitted_code = source_code
        session.execution_result = exec_result
        session.completed_at = datetime.now(timezone.utc)

        # Build visible-only results for response
        visible_results = [
            r for r in exec_result.get("results", [])
            if not r.get("is_hidden", False)
        ]

        capability_matrix = dict(user.capability_matrix or {})
        concept_id = session.concept_id

        # 5. Handle pass/fail
        if exec_result.get("all_passed"):
            session.outcome = "pass"

            # Update capability matrix — success
            capability_matrix = update_capability_on_success(
                capability_matrix, concept_id
            )
            user.capability_matrix = capability_matrix
            await db.flush()

            return {
                "outcome": "pass",
                "message": "All tests passed! 🎉",
                "results": visible_results,
            }
        else:
            session.outcome = "fail"

            # Update capability matrix — failure
            capability_matrix = update_capability_on_failure(
                capability_matrix, concept_id
            )
            user.capability_matrix = capability_matrix

            # 6. Generate Socratic hint
            hint = ""
            try:
                first_error = exec_result.get("first_error", "Unknown error")
                problem_desc = problem.get("description", "")
                hint = await self.socratic.guide(
                    source_code, first_error, problem_desc
                )
            except Exception as e:
                logger.error(f"Socratic Agent failed: {e}")
                hint = "Take a careful look at your code. What do you think might be causing the issue?"

            # Append hint to session
            hints = list(session.socratic_hints or [])
            hints.append(hint)
            session.socratic_hints = hints

            await db.flush()

            attempts = capability_matrix.get(concept_id, {}).get("attempts", 0)

            return {
                "outcome": "fail",
                "hint": hint,
                "results": visible_results,
                "attempts_on_concept": attempts,
            }

    async def check_backtrack(
        self,
        user_id: int,
        concept_id: str,
        db: AsyncSession,
    ) -> Optional[str]:
        """
        Check if the student should backtrack to a prerequisite.

        If the student has failed 3+ times on a concept, find the
        weakest prerequisite with mastery < 3.

        Returns:
            The concept_id to backtrack to, or None.
        """
        user_result = await db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            return None

        capability_matrix = user.capability_matrix or {}
        cap = capability_matrix.get(concept_id, {})

        if cap.get("failures", 0) >= 3:
            return self.knowledge_graph.find_backtrack_target(
                concept_id, capability_matrix
            )

        return None
