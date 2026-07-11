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

PROVIDER_MONITORING_SERVICE_ERROR_DATA = [
    {
        "error_type": "HTTPStatusError",
        "message": "apify.fetch_apify_balance failed: 401 Client Error: Unauthorized",
        "traceback": (
            "Traceback (most recent call last):\n"
            '  File "app/provider_monitoring/service/service.py", line 60, in run\n'
            "    result = fetcher()\n"
            '  File "app/provider_monitoring/apify.py", line 44, in fetch_apify_balance\n'
            "    response.raise_for_status()\n"
            "httpx.HTTPStatusError: 401 Client Error: Unauthorized"
        ),
        "provider_monitoring_service_log_id": 2,
    },
    {
        "error_type": "OperationalError",
        "message": "provider_monitoring_service run failed: could not connect to database",
        "traceback": (
            "Traceback (most recent call last):\n"
            '  File "app/provider_monitoring/service/service.py", line 52, in run\n'
            "    service_log = self.start_run(db)\n"
            "sqlalchemy.exc.OperationalError: could not connect to server: Connection refused"
        ),
        "level": "critical",
        "provider_monitoring_service_log_id": 3,
    },
    {
        "error_type": "ReadTimeout",
        "message": "anthropic.fetch_anthropic_daily_usage failed: HTTPSConnectionPool: Read timed out",
        "traceback": (
            "Traceback (most recent call last):\n"
            '  File "app/provider_monitoring/service/service.py", line 60, in run\n'
            "    result = fetcher()\n"
            '  File "app/provider_monitoring/anthropic.py", line 38, in fetch_anthropic_daily_usage\n'
            "    response = client.get(url, timeout=10)\n"
            "httpx.ReadTimeout: HTTPSConnectionPool: Read timed out"
        ),
        "provider_monitoring_service_log_id": 4,
    },
    {
        "error_type": "KeyError",
        "message": "brightdata.fetch_brightdata_balance failed: 'balance'",
        "traceback": (
            "Traceback (most recent call last):\n"
            '  File "app/provider_monitoring/service/service.py", line 60, in run\n'
            "    result = fetcher()\n"
            '  File "app/provider_monitoring/brightdata.py", line 51, in fetch_brightdata_balance\n'
            "    return data['balance']\n"
            "KeyError: 'balance'"
        ),
        "provider_monitoring_service_log_id": 4,
    },
]
