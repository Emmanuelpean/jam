"""Tests for the shared request_with_retry helper."""

from unittest.mock import MagicMock, patch

from utilities.http import MAX_ATTEMPTS, request_with_retry


def _resp(status_code: int) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = {}
    resp.text = "body"
    return resp


@patch("app.utilities.http.time.sleep")
@patch("app.utilities.http.requests.request")
class TestRequestWithRetry:
    def test_returns_immediately_on_success(self, mock_request, _mock_sleep) -> None:
        mock_request.return_value = _resp(200)

        resp = request_with_retry("GET", "https://x", service="svc")

        assert resp.status_code == 200
        assert mock_request.call_count == 1

    def test_retries_transient_then_succeeds(self, mock_request, _mock_sleep) -> None:
        mock_request.side_effect = [_resp(500), _resp(503), _resp(200)]

        resp = request_with_retry("GET", "https://x", service="svc")

        assert resp.status_code == 200
        assert mock_request.call_count == 3

    def test_gives_up_after_max_attempts(self, mock_request, mock_sleep) -> None:
        mock_request.return_value = _resp(500)

        resp = request_with_retry("GET", "https://x", service="svc")

        assert resp.status_code == 500
        assert mock_request.call_count == MAX_ATTEMPTS
        # No sleep after the final attempt.
        assert mock_sleep.call_count == MAX_ATTEMPTS - 1

    def test_does_not_retry_non_retryable_status(self, mock_request, mock_sleep) -> None:
        """A 400 (e.g. bad key / bad params) is returned immediately for the caller to raise."""

        mock_request.return_value = _resp(400)

        resp = request_with_retry("GET", "https://x", service="svc")

        assert resp.status_code == 400
        assert mock_request.call_count == 1
        assert mock_sleep.call_count == 0

    def test_honours_numeric_retry_after_header(self, mock_request, mock_sleep) -> None:
        retryable = _resp(429)
        retryable.headers = {"retry-after": "7"}
        mock_request.side_effect = [retryable, _resp(200)]

        request_with_retry("GET", "https://x", service="svc")

        mock_sleep.assert_called_once_with(7.0)

    def test_passes_method_url_and_kwargs_through(self, mock_request, _mock_sleep) -> None:
        mock_request.return_value = _resp(200)

        request_with_retry("POST", "https://x", service="svc", headers={"a": "b"}, json={"k": "v"}, timeout=5)

        args, kwargs = mock_request.call_args
        assert args == ("POST", "https://x")
        assert kwargs["headers"] == {"a": "b"}
        assert kwargs["json"] == {"k": "v"}
        assert kwargs["timeout"] == 5
