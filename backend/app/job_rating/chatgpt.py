"""AI scoring using OpenAI Chat Completions API."""

import json
import logging
from typing import Any

from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key)


class OpenAiError(Exception):
    """Raised when AI query fails."""


def openai_query(system_prompt: str, llm_prompt: str) -> dict[str, Any]:
    """Query openai chat completions API with constructed prompt.
    :param system_prompt: System prompt defining the AI's role.
    :param llm_prompt: Fully constructed prompt describing the job.
    return: parsed JSON output."""

    try:
        # noinspection PyTypeChecker
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": llm_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        content = response.choices[0].message.content

        if not content:
            raise OpenAiError("Empty response from OpenAI")

        try:
            return json.loads(content)

        except json.JSONDecodeError as exc:
            logger.error("Invalid JSON returned by OpenAI: %s", content)
            raise OpenAiError("Invalid JSON from OpenAI") from exc

    except Exception as exc:
        logger.exception("OpenAI query failed")
        raise OpenAiError from exc
