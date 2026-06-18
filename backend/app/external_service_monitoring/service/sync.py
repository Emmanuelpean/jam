"""Daily sync job: calls every fetch_* in this module and upserts the day-keyed results.
Each fetcher is run independently — one failure doesn't abort the others. Errors are logged
and recorded on the ServiceLog row, but the run is still marked is_success=False so admins
can spot partial failures."""

import datetime as dt
import traceback

from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ExternalServiceMonitoringServiceLog
from app.service_runner.service_runner import ServiceRunner
from app.external_service_monitoring.anthropic.fetch import fetch_anthropic_daily_usage
from app.external_service_monitoring.apify.fetch import fetch_apify_daily_usage, fetch_apify_balance
from app.external_service_monitoring.brightdata.fetch import fetch_brightdata_daily_usage, fetch_brightdata_balance
from app.external_service_monitoring.stripe.fetch import fetch_stripe_daily_income
from app.utilities import logger

SERVICE_NAME = "service_monitoring_service"

EXTERNAL_SERVICES = {
    "anthropic": [fetch_anthropic_daily_usage],
    "stripe": [fetch_stripe_daily_income],
    "apify": [fetch_apify_balance, fetch_apify_daily_usage],
    "brightdata": [fetch_brightdata_daily_usage, fetch_brightdata_balance],
}


class ServiceMonitor:
    """Runs all fetchers in sequence and upserts each into its own daily-history table."""

    def __init__(self) -> None:
        """Initialise the ServiceMonitor class"""

        self.logger = logger.AppLogger.create_service_logger(SERVICE_NAME, "INFO")

    def run(self, db: Session | None = None) -> None:
        """Fetch the different external services data
        :param db: Database session
        :return Service log entry"""

        db = next(get_db()) if db is None else db
        start = dt.datetime.now(dt.timezone.utc)
        service_log = ExternalServiceMonitoringServiceLog(run_datetime=start)
        db.add(service_log)
        db.commit()
        db.refresh(service_log)

        errors: list[str] = []
        try:
            for name in EXTERNAL_SERVICES:
                try:
                    self.logger.info(f"Fetching {name}")
                    for fetch_fn in EXTERNAL_SERVICES[name]:
                        fetch_fn(db)
                except Exception as exc:
                    db.rollback()
                    tb = traceback.format_exc()
                    self.logger.exception(f"{name} failed: {exc}")
                    errors.append(f"{name}: {exc}\n{tb}")
        finally:
            service_log.run_duration = (dt.datetime.now(dt.timezone.utc) - start).total_seconds()
            if errors:
                service_log.is_success = False
                service_log.error_message = "\n---\n".join(errors)
            else:
                service_log.is_success = True
            db.commit()
            db.refresh(service_log)
        return service_log


service_monitoring_runner = ServiceRunner(
    service_name=SERVICE_NAME,
    service_function=ServiceMonitor().run,
    period_hours=24,
)
