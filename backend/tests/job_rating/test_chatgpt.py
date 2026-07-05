"""Tests for app/job_rating/chatgpt.py — openai_query."""

import json
from unittest.mock import MagicMock, patch, AsyncMock

import pytest

from app.job_rating.chatgpt import OpenAiError, openai_query


def _make_response(content: str | None) -> MagicMock:
    """Build a mock OpenAI chat completion response."""
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.fixture(autouse=True)
def mock_openai_client():
    """Patch the module-level OpenAI client so no real HTTP calls are made."""
    with patch("app.job_rating.chatgpt.client") as mock_client:
        yield mock_client


class TestOpenaiQuery:

    def test_returns_parsed_json_on_success(self, mock_openai_client: MagicMock | AsyncMock) -> None:
        payload = {"score": 8, "reason": "Good fit"}
        mock_openai_client.chat.completions.create.return_value = _make_response(json.dumps(payload))

        result = openai_query("You are a helpful assistant.", "Rate this job.")

        assert result == payload

    def test_calls_correct_model(self, mock_openai_client: MagicMock | AsyncMock) -> None:
        mock_openai_client.chat.completions.create.return_value = _make_response("{}")

        openai_query("sys", "user")

        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4.1-mini"

    def test_sends_system_and_user_messages(self, mock_openai_client: MagicMock | AsyncMock) -> None:
        mock_openai_client.chat.completions.create.return_value = _make_response("{}")

        openai_query("My system prompt", "My user prompt")

        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        messages = call_kwargs["messages"]
        assert messages[0] == {"role": "system", "content": "My system prompt"}
        assert messages[1] == {"role": "user", "content": "My user prompt"}

    def test_requests_json_object_response_format(self, mock_openai_client: MagicMock | AsyncMock) -> None:
        mock_openai_client.chat.completions.create.return_value = _make_response("{}")

        openai_query("sys", "user")

        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["response_format"] == {"type": "json_object"}

    def test_temperature_is_0_2(self, mock_openai_client: MagicMock | AsyncMock) -> None:
        mock_openai_client.chat.completions.create.return_value = _make_response("{}")

        openai_query("sys", "user")

        call_kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.2

    def test_raises_openai_error_on_empty_content(self, mock_openai_client: MagicMock | AsyncMock) -> None:
        mock_openai_client.chat.completions.create.return_value = _make_response(None)

        with pytest.raises(OpenAiError):
            openai_query("sys", "user")

    def test_raises_openai_error_on_invalid_json(self, mock_openai_client: MagicMock | AsyncMock) -> None:
        mock_openai_client.chat.completions.create.return_value = _make_response("not valid json {{")

        with pytest.raises(OpenAiError):
            openai_query("sys", "user")

    def test_raises_openai_error_when_api_raises(self, mock_openai_client: MagicMock | AsyncMock) -> None:
        mock_openai_client.chat.completions.create.side_effect = RuntimeError("network error")

        with pytest.raises(OpenAiError):
            openai_query("sys", "user")

    def test_nested_json_parsed_correctly(self, mock_openai_client: MagicMock | AsyncMock) -> None:
        payload = {"scores": {"technical": 7, "culture": 9}, "tags": ["python", "remote"]}
        mock_openai_client.chat.completions.create.return_value = _make_response(json.dumps(payload))

        result = openai_query("sys", "user")

        assert result == payload
