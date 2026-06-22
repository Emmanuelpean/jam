"""AI scoring using Anthropic Claude Messages API."""

import json
import logging
import re
from typing import Any

from anthropic import Anthropic, APIStatusError

from app.config import settings

logger = logging.getLogger(__name__)

client = Anthropic(api_key=settings.anthropic_api_key)

MODEL = "claude-haiku-4-5-20251001"


class ClaudeError(Exception):
    """Raised when AI query fails."""


class ClaudeBillingError(ClaudeError):
    """Raised when the Anthropic account has insufficient credit / a billing problem.

    This is not a per-job failure — it affects every subsequent call until credits are topped
    up, so callers should abort the run and alert an admin rather than retry per job."""


def _is_billing_error(exc: Exception) -> bool:
    """Return True if the exception is an Anthropic insufficient-credit / billing error.
    :param exc: The exception raised by the Anthropic client."""

    if not isinstance(exc, APIStatusError):
        return False
    message = str(getattr(exc, "message", "") or exc).lower()
    return "credit balance is too low" in message or "plans & billing" in message


def claude_query(system_prompt: str, llm_prompt: str, max_tokens: int = 1024) -> dict[str, Any]:
    """Query Anthropic Claude Messages API with constructed prompt.
    :param system_prompt: System prompt defining the AI's role.
    :param llm_prompt: Fully constructed prompt describing the job.
    :param max_tokens: Maximum tokens in the response.
    return: parsed JSON output."""

    try:
        # noinspection PyTypeChecker
        response = client.messages.create(
            model=MODEL,
            system=[{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}],
            messages=[
                {"role": "user", "content": llm_prompt},
                {"role": "assistant", "content": "{"},  # forces JSON-only output
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )

        content = "{" + response.content[0].text

        if not content:
            raise ClaudeError("Empty response from Claude")

        # Strip Markdown code fences if present (e.g. ```json ... ```)
        stripped = re.sub(r"^```(?:json)?\s*\n?", "", content.strip())
        stripped = re.sub(r"\n?```\s*$", "", stripped).strip()

        try:
            return json.loads(stripped)

        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON returned by Claude: %s", content)
            raise ClaudeError("Invalid JSON from Claude") from exc

    except ClaudeError:
        raise
    except Exception as exc:
        logger.exception("Claude query failed")
        if _is_billing_error(exc):
            raise ClaudeBillingError(str(exc)) from exc
        raise ClaudeError from exc
