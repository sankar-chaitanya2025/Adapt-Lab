"""
Kimi API client utilities.

All three agents (Teacher, Generator, Socratic) use the Kimi API
(by Moonshot AI) via the OpenAI-compatible Python SDK.
"""

import json
import asyncio
import logging
from typing import Any, Dict, Optional

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)


def get_kimi_client() -> OpenAI:
    """
    Create and return an OpenAI client configured for the Kimi API.

    Returns:
        OpenAI client pointed at https://api.moonshot.cn/v1
    """
    return OpenAI(
        api_key=settings.KIMI_API_KEY,
        base_url="https://api.moonshot.cn/v1",
    )


def strip_code_fences(content: str) -> str:
    """
    Strip markdown code fences from LLM output.

    Handles patterns like:
        ```json\n{...}\n```
        ```\n{...}\n```
    """
    content = content.strip()
    if content.startswith("```"):
        # Remove first line (```json or ```)
        lines = content.split("\n", 1)
        if len(lines) > 1:
            content = lines[1]
        # Remove trailing ```
        if content.endswith("```"):
            content = content[:-3]
    return content.strip()


async def call_kimi_with_retry(
    client: OpenAI,
    messages: list,
    model: str = None,
    temperature: float = 0.3,
    max_retries: int = 3,
    parse_json: bool = True,
) -> Any:
    """
    Call the Kimi API with exponential backoff retry.

    Args:
        client: OpenAI client configured for Kimi API.
        messages: Chat messages to send.
        model: Model name (defaults to settings.KIMI_MODEL).
        temperature: Sampling temperature.
        max_retries: Maximum number of retry attempts.
        parse_json: If True, parse response as JSON.

    Returns:
        Parsed JSON dict/list or raw text string.

    Raises:
        Exception: After all retries are exhausted.
    """
    model = model or settings.KIMI_MODEL
    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            content = response.choices[0].message.content.strip()

            if parse_json:
                content = strip_code_fences(content)
                return json.loads(content)
            else:
                return content

        except json.JSONDecodeError as e:
            last_error = e
            logger.warning(
                f"JSON parse error on attempt {attempt + 1}/{max_retries}: {e}. "
                f"Raw response: {content[:500]}"
            )
        except Exception as e:
            last_error = e
            logger.warning(
                f"Kimi API error on attempt {attempt + 1}/{max_retries}: {e}"
            )

        # Exponential backoff: 1s, 2s, 4s
        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logger.info(f"Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

    logger.error(f"All {max_retries} Kimi API attempts failed. Last error: {last_error}")
    raise last_error
