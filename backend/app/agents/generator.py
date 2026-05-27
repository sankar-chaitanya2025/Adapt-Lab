"""
Generator Agent — The Creator.

Receives a directive from the Teacher Agent and generates
a unique C programming problem with test cases.
"""

import json
import logging
from typing import Dict, Any

from app.agents import get_kimi_client, call_kimi_with_retry
from app.config import settings

logger = logging.getLogger(__name__)

GENERATOR_SYSTEM_PROMPT = """You are the Generator Agent in an adaptive C programming tutoring system called AdaptLab.

Your role is to create unique, well-crafted C programming problems based on a directive from the Teacher Agent. Each problem must precisely target the specified concept, difficulty level, and focus area.

RULES:
The problem MUST test the exact concept and focus area specified in the directive.
Difficulty level 1 = basic syntax/usage, level 2 = simple application, level 3 = moderate problem-solving, level 4 = complex multi-step, level 5 = edge cases and optimization.
Always provide starter code that compiles but is incomplete — the student fills in the logic.
Provide exactly 3 visible test cases and 2 hidden test cases.
Test cases must have clear, deterministic expected output.
The problem must be solvable with ONLY the concepts at or below the target concept's level in the curriculum.
Do NOT use any C features beyond what the target concept and its prerequisites cover.

You MUST respond with ONLY a valid JSON object in this exact format, with no additional text, no markdown, no explanation:

{
  "title": "<short descriptive title>",
  "description": "<clear problem statement, 2-4 sentences>",
  "starter_code": "<compilable C code with TODO comments where student writes code>",
  "test_cases": {
    "visible": [
      {"input": "<stdin input>", "expected_output": "<exact expected stdout>"},
      {"input": "<stdin input>", "expected_output": "<exact expected stdout>"},
      {"input": "<stdin input>", "expected_output": "<exact expected stdout>"}
    ],
    "hidden": [
      {"input": "<stdin input>", "expected_output": "<exact expected stdout>"},
      {"input": "<stdin input>", "expected_output": "<exact expected stdout>"}
    ]
  },
  "concept_id": "<concept_id from directive>",
  "difficulty": <integer from directive>
}"""


class GeneratorAgent:
    """Problem creator that generates C programming problems from Teacher directives."""

    def __init__(self):
        self.client = get_kimi_client()
        self.system_prompt = GENERATOR_SYSTEM_PROMPT

    async def generate(self, teacher_directive: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a C programming problem based on the Teacher's directive.

        Args:
            teacher_directive: Dict with TARGET_TOPIC, TARGET_LEVEL, FOCUS_AREA, REASONING.

        Returns:
            Dict with keys: title, description, starter_code, test_cases, concept_id, difficulty.
        """
        user_message = f"""Teacher Directive:
{json.dumps(teacher_directive, indent=2)}

Generate a C programming problem that follows this directive exactly."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

        result = await call_kimi_with_retry(
            client=self.client,
            messages=messages,
            temperature=0.7,
            parse_json=True,
        )

        # Validate required keys
        required_keys = ["title", "description", "starter_code", "test_cases", "concept_id", "difficulty"]
        for key in required_keys:
            if key not in result:
                logger.warning(f"Generator Agent response missing key: {key}")
                raise ValueError(f"Generator Agent response missing required key: {key}")

        # Validate test_cases structure
        tc = result.get("test_cases", {})
        if "visible" not in tc or "hidden" not in tc:
            raise ValueError("Generator Agent response missing visible/hidden test cases")
        if len(tc["visible"]) < 1:
            raise ValueError("Generator Agent must provide at least 1 visible test case")

        logger.info(
            f"Generated problem: '{result['title']}' for concept={result['concept_id']}, "
            f"difficulty={result['difficulty']}"
        )

        return result
