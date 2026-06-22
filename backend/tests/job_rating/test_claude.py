"""Tests for app/job_rating/claude.py — claude_query."""

import json
from unittest.mock import MagicMock, patch

import pytest

import httpx
from anthropic import BadRequestError

from app.job_rating.claude import ClaudeBillingError, ClaudeError, claude_query

# -------------------------------------------------- HELPERS ---------------------------------------------------


def _make_response(text: str) -> MagicMock:
    """Build a mock Anthropic Messages response whose first content block has the given text."""
    block = MagicMock()
    block.text = text
    response = MagicMock()
    response.content = [block]
    return response


# -------------------------------------------------- FIXTURE ---------------------------------------------------


@pytest.fixture(autouse=True)
def mock_anthropic_client():
    """Patch the module-level Anthropic client so no real HTTP calls are made."""
    with patch("app.job_rating.claude.client") as mock_client:
        yield mock_client


# --------------------------------------------------- TESTS ----------------------------------------------------


class TestClaudeQuery:

    def test_returns_parsed_json_on_success(self, mock_anthropic_client) -> None:
        # The module prepends "{" to response.content[0].text, so the mock text
        # should be the JSON body WITHOUT the opening brace.
        payload = {"score": 8, "reason": "Good fit"}
        raw_json = json.dumps(payload)
        mock_anthropic_client.messages.create.return_value = _make_response(raw_json[1:])  # drop leading "{"

        result = claude_query("You are a helpful assistant.", "Rate this job.")

        assert result == payload

    def test_calls_correct_model(self, mock_anthropic_client) -> None:
        mock_anthropic_client.messages.create.return_value = _make_response("}")

        claude_query("sys", "user")

        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-haiku-4-5-20251001"

    def test_sends_system_prompt_with_cache_control(self, mock_anthropic_client) -> None:
        mock_anthropic_client.messages.create.return_value = _make_response("}")

        claude_query("My system prompt", "user")

        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert call_kwargs["system"] == [
            {"type": "text", "text": "My system prompt", "cache_control": {"type": "ephemeral"}}
        ]

    def test_sends_user_message_and_assistant_prefix(self, mock_anthropic_client) -> None:
        mock_anthropic_client.messages.create.return_value = _make_response("}")

        claude_query("sys", "My user prompt")

        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        messages = call_kwargs["messages"]
        assert messages[0] == {"role": "user", "content": "My user prompt"}
        assert messages[1] == {"role": "assistant", "content": "{"}

    def test_temperature_is_0_2(self, mock_anthropic_client) -> None:
        mock_anthropic_client.messages.create.return_value = _make_response("}")

        claude_query("sys", "user")

        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.2

    def test_default_max_tokens_is_1024(self, mock_anthropic_client) -> None:
        mock_anthropic_client.messages.create.return_value = _make_response("}")

        claude_query("sys", "user")

        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert call_kwargs["max_tokens"] == 1024

    def test_custom_max_tokens_passed_through(self, mock_anthropic_client) -> None:
        mock_anthropic_client.messages.create.return_value = _make_response("}")

        claude_query("sys", "user", max_tokens=2048)

        call_kwargs = mock_anthropic_client.messages.create.call_args.kwargs
        assert call_kwargs["max_tokens"] == 2048

    def test_json_with_whitespace_parsed_correctly(self, mock_anthropic_client) -> None:
        # content = "{" + text; test that leading/trailing whitespace in the combined
        # string is stripped before JSON parsing.
        payload = {"score": 5}
        raw = json.dumps(payload)
        # Provide text with trailing whitespace so content = raw + "  "
        mock_anthropic_client.messages.create.return_value = _make_response(raw[1:] + "  ")

        result = claude_query("sys", "user")

        assert result == payload

    def test_empty_json_object_parsed_correctly(self, mock_anthropic_client) -> None:
        # content = "{" + "}" = "{}"
        mock_anthropic_client.messages.create.return_value = _make_response("}")

        result = claude_query("sys", "user")

        assert result == {}

    def test_raises_claude_error_on_invalid_json(self, mock_anthropic_client) -> None:
        mock_anthropic_client.messages.create.return_value = _make_response("not valid json {{")

        with pytest.raises(ClaudeError):
            claude_query("sys", "user")

    def test_raises_claude_error_when_api_raises(self, mock_anthropic_client) -> None:
        mock_anthropic_client.messages.create.side_effect = RuntimeError("network error")

        with pytest.raises(ClaudeError):
            claude_query("sys", "user")

    def test_raises_billing_error_on_insufficient_credit(self, mock_anthropic_client) -> None:
        """An Anthropic insufficient-credit 400 is classified as ClaudeBillingError (a ClaudeError
        subclass), so callers can distinguish it from a per-job failure."""

        body = {
            "type": "error",
            "error": {
                "type": "invalid_request_error",
                "message": "Your credit balance is too low to access the Anthropic API. "
                "Please go to Plans & Billing to upgrade or purchase credits.",
            },
        }
        request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        response = httpx.Response(400, request=request, json=body)
        mock_anthropic_client.messages.create.side_effect = BadRequestError(
            "credit balance is too low", response=response, body=body
        )

        with pytest.raises(ClaudeBillingError):
            claude_query("sys", "user")

    def test_generic_bad_request_is_not_billing_error(self, mock_anthropic_client) -> None:
        """A non-billing 400 stays a plain ClaudeError, not a ClaudeBillingError."""

        body = {"type": "error", "error": {"type": "invalid_request_error", "message": "bad model"}}
        request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        response = httpx.Response(400, request=request, json=body)
        mock_anthropic_client.messages.create.side_effect = BadRequestError("bad model", response=response, body=body)

        with pytest.raises(ClaudeError) as exc_info:
            claude_query("sys", "user")
        assert not isinstance(exc_info.value, ClaudeBillingError)

    def test_nested_json_parsed_correctly(self, mock_anthropic_client) -> None:
        payload = {"scores": {"technical": 7, "culture": 9}, "tags": ["python", "remote"]}
        raw_json = json.dumps(payload)
        mock_anthropic_client.messages.create.return_value = _make_response(raw_json[1:])

        result = claude_query("sys", "user")

        assert result == payload
