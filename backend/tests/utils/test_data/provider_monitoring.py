"""Test data for the provider monitoring service."""

import datetime as dt

from tests.utils.test_data.utils import CURRENT_DATE, DATETIME_FORMAT

# ------------------------------------------ PROVIDER MONITORING SERVICE LOGS -------------------------------------------

# The ProviderMonitoringServiceLog has no extra columns of its own; a run is just a timestamp and a duration. Its
# is_success is derived purely from whether any linked ServiceError is CRITICAL.
PROVIDER_MONITORING_SERVICE_LOG_DATA = [
    {
        "run_duration": 4.2,
        "run_datetime": "2025-01-15T06:00:00+00:00",
    },
    {
        "run_duration": 5.8,
        "run_datetime": "2025-01-16T06:00:00+00:00",
    },
    {
        "run_duration": 1.1,
        "run_datetime": "2025-01-17T06:00:00+00:00",
    },
    {
        "run_duration": 6.5,
        "run_datetime": "2025-01-18T06:00:00+00:00",
    },
]

SERVICE_LOG_DATETIME = [CURRENT_DATE - dt.timedelta(days=i) for i in range(len(PROVIDER_MONITORING_SERVICE_LOG_DATA))]
for service_log, date in zip(PROVIDER_MONITORING_SERVICE_LOG_DATA, SERVICE_LOG_DATETIME):
    service_log["run_datetime"] = date.strftime(DATETIME_FORMAT)


# ----------------------------------------- PROVIDER MONITORING SERVICE ERRORS ------------------------------------------

# Per-fetcher failures are ERROR level (one fetcher failing does not fail the run); a run-level abort is CRITICAL and
# drives the run's derived is_success to False. provider_monitoring_service_log_id is the 1-based position of the
# run in PROVIDER_MONITORING_SERVICE_LOG_DATA.
PROVIDER_MONITORING_SERVICE_ERROR_DATA = [
    # Run 2: a single fetcher failed, the rest of the run completed (is_success stays True).
    {
        "error_type": "HTTPStatusError",
        "message": "apify.fetch_apify_balance failed: 401 Client Error: Unauthorized",
        "provider_monitoring_service_log_id": 2,
    },
    # Run 3: the whole run aborted before/while fetching (is_success False).
    {
        "error_type": "OperationalError",
        "message": "provider_monitoring_service run failed: could not connect to database",
        "level": "critical",
        "provider_monitoring_service_log_id": 3,
    },
    # Run 4: two independent fetchers failed but the run still finished (is_success stays True).
    {
        "error_type": "ReadTimeout",
        "message": "anthropic.fetch_anthropic_daily_usage failed: HTTPSConnectionPool: Read timed out",
        "provider_monitoring_service_log_id": 4,
    },
    {
        "error_type": "KeyError",
        "message": "brightdata.fetch_brightdata_balance failed: 'balance'",
        "provider_monitoring_service_log_id": 4,
    },
]
