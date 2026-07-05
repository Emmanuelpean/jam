from unittest.mock import MagicMock, patch

import pytest

from utils.test_data.geolocation import MOCK_GEOCODING_RESPONSES


@pytest.fixture(autouse=True)
def block_real_apify_client():
    """Safety net: no test may construct a real ApifyClient, which would hit the live Apify API.
    Tests that exercise Apify scrapers patch ApifyClient themselves; this makes an un-mocked
    construction fail loudly instead of reaching the network."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real ApifyClient constructed in a test - patch "
            "'app.job_email_scraping.job_scrapers.apify.ApifyClient' in your test or fixture."
        )

    with patch("app.job_email_scraping.job_scrapers.apify.ApifyClient", side_effect=fail):
        yield


@pytest.fixture(autouse=True)
def block_real_brightdata_requests():
    """Safety net: no test may make a real BrightData HTTP request, which would hit the live API.
    Tests that exercise BrightData scrapers patch the scraper's `requests` themselves; this makes an
    un-mocked request fail loudly instead of reaching the network."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real BrightData HTTP request in a test - patch "
            "'app.job_email_scraping.job_scrapers.brightdata.requests' in your test or fixture."
        )

    mock_requests = MagicMock()
    mock_requests.get.side_effect = fail
    mock_requests.post.side_effect = fail
    with patch("app.job_email_scraping.job_scrapers.brightdata.requests", mock_requests):
        yield


@pytest.fixture(autouse=True)
def block_real_openai_client():
    """Safety net: no test may reach the live OpenAI API. Tests that exercise job rating patch the
    client themselves; this makes an un-mocked chat completion fail loudly instead of hitting the network.

    Guards both the already-constructed module-level client and the ``OpenAI`` class itself, so any
    client built during a test (now or in future code paths) is also a loud mock."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real OpenAI request in a test - patch 'app.job_rating.chatgpt.client' in your test or fixture."
        )

    def make_loud_client(*_args, **_kwargs):
        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = fail
        return mock_client

    with (
        patch("app.job_rating.chatgpt.client", make_loud_client()),
        patch("openai.OpenAI", side_effect=make_loud_client),
    ):
        yield


@pytest.fixture(autouse=True)
def block_real_anthropic_client():
    """Safety net: no test may reach the live Anthropic API. Tests that exercise job rating patch the
    client themselves; this makes an un-mocked message create fail loudly instead of hitting the network.

    Guards both the already-constructed module-level client and the ``Anthropic`` class itself, so any
    client built during a test (now or in future code paths) is also a loud mock."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real Anthropic request in a test - patch 'app.job_rating.claude.client' in your test or fixture."
        )

    def make_loud_client(*_args, **_kwargs):
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = fail
        return mock_client

    with (
        patch("app.job_rating.claude.client", make_loud_client()),
        patch("anthropic.Anthropic", side_effect=make_loud_client),
    ):
        yield


@pytest.fixture(autouse=True)
def block_real_provider_http():
    """Safety net for provider-monitoring fetchers (Anthropic cost_report, Apify, BrightData, Stripe),
    which all reach the network through `request_with_retry` -> `requests.request` in app.utilities.http.
    Tests patch `request_with_retry` in each fetch module; this blocks the transport underneath so any
    un-mocked fetch fails loudly instead of hitting the live provider API."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real provider HTTP request in a test - patch 'request_with_retry' in the relevant "
            "app.provider_monitoring.*.fetch module in your test or fixture."
        )

    mock_requests = MagicMock()
    mock_requests.request.side_effect = fail
    with patch("app.utilities.http.requests", mock_requests):
        yield


@pytest.fixture(autouse=True)
def block_real_stripe_requests():
    """Safety net: no test may reach the live Stripe API through the SDK. The payments code calls the
    Stripe SDK directly (e.g. `stripe.Customer.create_async`), and every typed call funnels through
    `_APIRequestor.request`/`request_async`. Tests patch the specific SDK method they exercise; this
    blocks the transport underneath so any un-mocked call fails loudly instead of hitting the network."""

    def fail(*_args, **_kwargs):
        raise RuntimeError(
            "Real Stripe request in a test - patch the specific 'stripe.*' SDK call "
            "(e.g. 'app.payments.customer.stripe.Customer.retrieve_async') in your test or fixture."
        )

    with (
        patch("stripe._api_requestor._APIRequestor.request", side_effect=fail),
        patch("stripe._api_requestor._APIRequestor.request_async", side_effect=fail),
    ):
        yield


@pytest.fixture(autouse=True)
def mock_nominatim_get():
    """Auto-mock Nominatim HTTP calls using MOCK_GEOCODING_RESPONSES.
    Known queries return a real-shaped Nominatim response; unknown queries return []
    which causes call_geocoding_api to raise ValueError."""

    def side_effect(url, **kwargs):
        """Mock the requests.get call to Nominatim."""
        _ = url
        params = kwargs.get("params", {})
        query = params.get("q")
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = MOCK_GEOCODING_RESPONSES.get(query, [])
        return mock_response

    with (
        patch("app.geolocation.geolocation.requests.get", side_effect=side_effect) as mock,
        patch("app.geolocation.geolocation.time.sleep"),
    ):
        yield mock
