"""Daily sync job: calls every fetch_* in this module and upserts the day-keyed results.
Each fetcher is run independently — one failure doesn't abort the others. Transient failures are
absorbed by the HTTP-level retries in request_with_retry, and the next daily run re-fetches the
full window anyway, so there is no cross-run retry here. Every failure is recorded as an Error,
and the run is marked is_success=False whenever a fetcher fails so admins can spot partial
failures."""

import datetime as dt
import traceback

from sqlalchemy.orm import Session

from app.database import get_db
from app.external_service_monitoring.anthropic.fetch import fetch_anthropic_daily_usage
from app.external_service_monitoring.apify.fetch import fetch_apify_daily_usage, fetch_apify_balance
from app.external_service_monitoring.brightdata.fetch import fetch_brightdata_daily_usage, fetch_brightdata_balance
from app.external_service_monitoring import logger
from app.external_service_monitoring.stripe.fetch import fetch_stripe_daily_income
from app.models import ExternalServiceMonitoringServiceLog
from app.service_runner.models import record_error
from app.service_runner.service_runner import ServiceRunner

SERVICE_NAME = "service_monitoring_service"

EXTERNAL_SERVICES = {
    "anthropic": [fetch_anthropic_daily_usage],
    "stripe": [fetch_stripe_daily_income],
    "apify": [fetch_apify_balance, fetch_apify_daily_usage],
    "brightdata": [fetch_brightdata_daily_usage, fetch_brightdata_balance],
}


class ServiceMonitor:
    """Runs all fetchers in sequence and upserts each into its own daily-history table."""

    @staticmethod
    def run(db: Session | None = None) -> ExternalServiceMonitoringServiceLog:
        """Fetch the different external services data
        :param db: Database session
        :return Service log entry"""

        db = next(get_db()) if db is None else db
        start = dt.datetime.now(dt.timezone.utc)
        service_log = ExternalServiceMonitoringServiceLog(run_datetime=start)
        db.add(service_log)
        db.commit()
        db.refresh(service_log)
        logger.info(f"Starting {SERVICE_NAME} run")

        errors: list[str] = []
        for name, fetch_fns in EXTERNAL_SERVICES.items():
            for fetch_fn in fetch_fns:
                label = f"{name}.{fetch_fn.__name__}"
                try:
                    logger.info(f"Fetching {label}")
                    fetch_fn(db)
                except Exception as exc:
                    db.rollback()
                    message = f"{label} failed: {exc}"
                    logger.exception(message)
                    record_error(db, exc, message=message, external_service_monitoring_service_log_id=service_log.id)
                    errors.append(f"{label}: {exc}\n{traceback.format_exc()}")

        service_log.run_duration = (dt.datetime.now(dt.timezone.utc) - start).total_seconds()
        if errors:
            service_log.is_success = False
            service_log.error_message = "\n---\n".join(errors)
        else:
            service_log.is_success = True
        db.commit()
        db.refresh(service_log)
        logger.info(f"Finished {SERVICE_NAME} run")
        return service_log


service_monitoring_runner = ServiceRunner(
    service_name=SERVICE_NAME,
    service_function=ServiceMonitor().run,
    period_hours=24,
)
