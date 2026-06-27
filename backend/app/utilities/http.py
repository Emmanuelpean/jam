"""Shared HTTP helper for provider-monitoring fetchers.

Providers' usage/billing endpoints (Anthropic Admin cost_report, Apify, Bright Data) are
intermittently flaky and return transient 5xx/429s. This wraps `requests` with exponential
backoff and logs the response body on any error — providers put the real reason there, and
`raise_for_status` discards it."""

import logging
import time

import requests

RETRY_STATUSES = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = 4
BACKOFF_BASE_SECONDS = 1.0


def request_with_retry(
    method: str,
    url: str,
    *,
    service: str,
    headers: dict | None = None,
    params: dict | None = None,
    json: dict | None = None,
    timeout: int = 10,
    logger: logging.Logger | None = None,
) -> requests.Response:
    """HTTP request with exponential backoff on transient (5xx/429) responses.

    Retryable statuses are retried up to MAX_ATTEMPTS; the final response is returned for the
    caller to `raise_for_status`, so non-retryable errors (e.g. a 401 from a bad key) surface
    immediately and unchanged. The response body is logged on every error status.
    :param method: HTTP method (e.g. "GET", "POST").
    :param url: Request URL.
    :param service: Service label for log lines (e.g. "anthropic").
    :param headers: Request headers.
    :param params: Query parameters.
    :param json: JSON request body.
    :param timeout: Per-request timeout in seconds.
    :param logger: Optional logger for log lines."""

    resp = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        resp = requests.request(method, url, headers=headers, params=params, json=json, timeout=timeout)
        if resp.status_code < 400:
            return resp

        if logger:
            logger.warning(
                f"{service} {method} {url} failed (attempt {attempt:d}/{MAX_ATTEMPTS:d})"
                f": {resp.status_code} {resp.text}",
            )
        if resp.status_code not in RETRY_STATUSES or attempt == MAX_ATTEMPTS:
            break

        retry_after = resp.headers.get("retry-after")
        if retry_after and retry_after.isdigit():
            delay = float(retry_after)
        else:
            delay = BACKOFF_BASE_SECONDS * 2 ** (attempt - 1)
        time.sleep(delay)

    if not resp:
        raise RuntimeError(f"Failed to fetch {service} data after {MAX_ATTEMPTS:d} attempts")

    return resp
