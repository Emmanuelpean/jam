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

# Errors mirror those recorded by ProviderMonitoringService in app/provider_monitoring/service/service.py:
# each failed fetch records the static "Provider fetch failed." (error_type = the caught exception) with the
# provider label and error text in `context`; an exception escaping the fetch loop records the CRITICAL
# "Critical error in provider monitoring workflow".
PROVIDER_MONITORING_SERVICE_ERROR_DATA = [
    {
        "error_type": "HTTPStatusError",
        "message": "Provider fetch failed.",
        "context": {
            "provider": "apify.fetch_apify_balance",
            "error": "Client error '401 Unauthorized' for url 'https://api.apify.com/v2/users/me'",
        },
        "traceback": (
            "Traceback (most recent call last):\n"
            '  File "app/provider_monitoring/service/service.py", line 54, in run\n'
            "    fetch_fn(db, self.logger)\n"
            '  File "app/provider_monitoring/apify/fetch.py", line 44, in fetch_apify_balance\n'
            "    response.raise_for_status()\n"
            "httpx.HTTPStatusError: Client error '401 Unauthorized' for url 'https://api.apify.com/v2/users/me'"
        ),
        "provider_monitoring_service_log_id": 2,
    },
    {
        "error_type": "ReadTimeout",
        "message": "Provider fetch failed.",
        "context": {"provider": "anthropic.fetch_anthropic_daily_usage", "error": "The read operation timed out"},
        "traceback": (
            "Traceback (most recent call last):\n"
            '  File "app/provider_monitoring/service/service.py", line 54, in run\n'
            "    fetch_fn(db, self.logger)\n"
            '  File "app/provider_monitoring/anthropic/fetch.py", line 52, in fetch_anthropic_daily_usage\n'
            "    response = client.get(url, timeout=10)\n"
            "httpx.ReadTimeout: The read operation timed out"
        ),
        "provider_monitoring_service_log_id": 4,
    },
    {
        "error_type": "KeyError",
        "message": "Provider fetch failed.",
        "context": {"provider": "brightdata.fetch_brightdata_balance", "error": "'balance'"},
        "traceback": (
            "Traceback (most recent call last):\n"
            '  File "app/provider_monitoring/service/service.py", line 54, in run\n'
            "    fetch_fn(db, self.logger)\n"
            '  File "app/provider_monitoring/brightdata/fetch.py", line 78, in fetch_brightdata_balance\n'
            "    return data['balance']\n"
            "KeyError: 'balance'"
        ),
        "provider_monitoring_service_log_id": 4,
    },
    # Critical: a DB failure while persisting a fetch error escapes the inner handler and aborts the run.
    {
        "error_type": "OperationalError",
        "message": "Critical error in provider monitoring workflow",
        "traceback": (
            "Traceback (most recent call last):\n"
            '  File "app/provider_monitoring/service/service.py", line 58, in run\n'
            "    record_error(\n"
            '  File "app/service/models.py", line 200, in record_error\n'
            "    db.commit()\n"
            "sqlalchemy.exc.OperationalError: (psycopg2.errors.AdminShutdown) terminating connection due to "
            "administrator command"
        ),
        "level": "critical",
        "provider_monitoring_service_log_id": 3,
    },
]
