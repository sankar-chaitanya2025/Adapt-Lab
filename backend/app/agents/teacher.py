"""
Teacher Agent — The Strategist.

Analyzes the student's capability matrix and decides what topic
and difficulty level to target next.
"""

import json
import logging
from typing import Dict, Any

from app.agents import get_kimi_client, call_kimi_with_retry
from app.config import settings

logger = logging.getLogger(__name__)

TEACHER_SYSTEM_PROMPT = """You are the Teacher Agent in an adaptive C programming tutoring system called AdaptLab.

Your role is to act as a curriculum strategist. You analyze a student's capability matrix (a JSON object showing mastery levels, attempts, successes, and failures for each C programming concept) and the current knowledge graph structure to decide what the student should work on next.

RULES:
If the student has concepts at status "struggling" (2+ consecutive failures), you MUST target the weakest prerequisite of that concept for review.
If all attempted concepts are at healthy mastery, advance to the next unlocked concept at the appropriate difficulty level.
Never skip prerequisites. A concept can only be targeted if ALL its prerequisites have mastery_level >= 3.
Difficulty levels range from 1 (easiest) to 5 (hardest). Increase difficulty by 1 on success, decrease by 1 on failure (minimum 1).
Always pick exactly ONE concept to focus on.

You MUST respond with ONLY a valid JSON object in this exact format, with no additional text, no markdown, no explanation:

{
  "TARGET_TOPIC": "<concept_id>",
  "TARGET_LEVEL": <integer 1-5>,
  "FOCUS_AREA": "<specific sub-skill or common mistake to focus the problem on>",
  "REASONING": "<one sentence explaining your decision>"
}"""


class TeacherAgent:
    """Curriculum strategist that decides the next concept and difficulty."""

    def __init__(self):
        self.client = get_kimi_client()
        self.system_prompt = TEACHER_SYSTEM_PROMPT

    async def decide_next(
        self,
        capability_matrix: Dict[str, Any],
        knowledge_graph_summary: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analyze student state and decide what to teach next.

        Args:
            capability_matrix: Student's full capability matrix (concept → stats).
            knowledge_graph_summary: Dict of concept_id → list of prerequisite IDs.

        Returns:
            Dict with keys: TARGET_TOPIC, TARGET_LEVEL, FOCUS_AREA, REASONING.
        """
        user_message = f"""Student Capability Matrix:
{json.dumps(capability_matrix, indent=2)}

Knowledge Graph Structure (concept -> prerequisites):
{json.dumps(knowledge_graph_summary, indent=2)}

Analyze the student's current state and decide what they should work on next."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

        result = await call_kimi_with_retry(
            client=self.client,
            messages=messages,
            temperature=0.3,
            parse_json=True,
        )

        # Validate required keys
        required_keys = ["TARGET_TOPIC", "TARGET_LEVEL", "FOCUS_AREA", "REASONING"]
        for key in required_keys:
            if key not in result:
                logger.warning(f"Teacher Agent response missing key: {key}")
                raise ValueError(f"Teacher Agent response missing required key: {key}")

        logger.info(
            f"Teacher directive: topic={result['TARGET_TOPIC']}, "
            f"level={result['TARGET_LEVEL']}, focus={result['FOCUS_AREA']}"
        )

        return result
