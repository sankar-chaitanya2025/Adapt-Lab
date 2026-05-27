"""
Socratic Agent — The Coach.

Analyzes failed submissions and provides Socratic guidance
without ever revealing the answer.
"""

import logging
from typing import Optional

from app.agents import get_kimi_client, call_kimi_with_retry
from app.config import settings

logger = logging.getLogger(__name__)

SOCRATIC_SYSTEM_PROMPT = """You are the Socratic Agent in an adaptive C programming tutoring system called AdaptLab.

Your role is to help students learn from their mistakes by asking guiding questions. You analyze their failed code submission and the compiler/runtime errors to craft a Socratic question that leads them toward understanding their mistake.

ABSOLUTE RULES:
You MUST NEVER write, fix, correct, or provide any C code. Not a single line. Not even pseudocode.
You MUST NEVER directly tell the student what the error is or what the fix is.
Your response MUST be exactly 1-3 sentences long.
You MUST phrase your guidance as a QUESTION that makes the student think.
Focus on the conceptual misunderstanding, not the syntax.
If the error is a compilation error, guide them to understand what the compiler is telling them.
If the error is a logic error (wrong output), guide them to trace through their logic.

GOOD EXAMPLE: "What value do you think x holds after line 5 executes? Try tracing through the loop with the first test input."
BAD EXAMPLE: "You need to change the loop condition from < to <=."

Respond with ONLY your Socratic question. No JSON, no formatting, no preamble — just the question text."""


class SocraticAgent:
    """Socratic coach that guides students with questions, never answers."""

    def __init__(self):
        self.client = get_kimi_client()
        self.system_prompt = SOCRATIC_SYSTEM_PROMPT

    async def guide(
        self,
        submitted_code: str,
        error_output: str,
        problem_description: str,
    ) -> str:
        """
        Generate a Socratic hint based on a failed submission.

        Args:
            submitted_code: The student's C code that failed.
            error_output: Compiler error, stderr, or test mismatch info.
            problem_description: The original problem statement.

        Returns:
            A 1-3 sentence Socratic question as a string.
        """
        user_message = f"""Problem Description:
{problem_description}

Student's Submitted Code:
```c
{submitted_code}
```

Error / Test Result:
{error_output}

Provide a Socratic question to help the student understand their mistake."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message},
        ]

        result = await call_kimi_with_retry(
            client=self.client,
            messages=messages,
            temperature=0.5,
            parse_json=False,
        )

        # Truncate to 3 sentences max
        hint = self._truncate_to_sentences(result, max_sentences=3)

        logger.info(f"Socratic hint generated ({len(hint)} chars)")
        return hint

    @staticmethod
    def _truncate_to_sentences(text: str, max_sentences: int = 3) -> str:
        """Truncate text to at most max_sentences sentences."""
        text = text.strip()
        sentences = []
        current = ""

        for char in text:
            current += char
            if char in ".?!":
                sentences.append(current.strip())
                current = ""
                if len(sentences) >= max_sentences:
                    break

        # If we didn't hit any sentence-ending punctuation, return as-is
        if not sentences:
            return text

        return " ".join(sentences)
