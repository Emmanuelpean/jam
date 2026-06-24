"""Daily sync job: calls every fetch_* in this module and upserts the day-keyed results.
Each fetcher is run independently — one failure doesn't abort the others. Transient failures are
absorbed by the HTTP-level retries in request_with_retry, and the next daily run re-fetches the
full window anyway, so there is no cross-run retry here. Every failure is recorded as an Error so
admins can spot partial failures (a run's derived ``is_success`` only flips to False on a critical
error)."""

from sqlalchemy.orm import Session

from app.external_service_monitoring.anthropic.fetch import fetch_anthropic_daily_usage
from app.external_service_monitoring.apify.fetch import fetch_apify_daily_usage, fetch_apify_balance
from app.external_service_monitoring.brightdata.fetch import fetch_brightdata_daily_usage, fetch_brightdata_balance
from app.external_service_monitoring.stripe.fetch import fetch_stripe_daily_income
from app.models import ExternalServiceMonitoringServiceLog
from app.service_runner.models import ErrorLevel, record_error
from app.service_runner.service import Service
from app.service_runner.service_runner import ServiceRunner


class EsmService(Service[ExternalServiceMonitoringServiceLog]):
    """Runs all fetchers in sequence and upserts each into its own daily-history table."""

    service_name = "service_monitoring_service"

    def __init__(self):
        """Initialise the service"""

        Service.__init__(self, ExternalServiceMonitoringServiceLog)
        self.external_services = {
            "anthropic": [fetch_anthropic_daily_usage],
            "stripe": [fetch_stripe_daily_income],
            "apify": [fetch_apify_balance, fetch_apify_daily_usage],
            "brightdata": [fetch_brightdata_daily_usage, fetch_brightdata_balance],
        }

    def run(self, db: Session | None = None) -> ExternalServiceMonitoringServiceLog:
        """Fetch the different external services data
        :param db: Database session
        :return Service log entry"""

        service_log, db = self.start_run(db)

        try:
            for name, fetch_fns in self.external_services.items():
                for fetch_fn in fetch_fns:
                    label = f"{name}.{fetch_fn.__name__}"
                    try:
                        self.logger.info(f"Fetching {label}")
                        fetch_fn(db, self.logger)
                    except Exception as exc:
                        message = f"{label} failed: {exc}"
                        self.logger.exception(message)
                        record_error(
                            db=db,
                            exc=exc,
                            message=message,
                            external_service_monitoring_service_log_id=service_log.id,
                        )
        except Exception as exc:
            self.logger.exception(f"Critical error in {self.service_name} run: {exc}")
            record_error(db, exc, level=ErrorLevel.CRITICAL, external_service_monitoring_service_log_id=service_log.id)
        service_log.set_run_duration()
        db.commit()
        db.refresh(service_log)
        self.logger.info(f"Finished {self.service_name} run")
        return service_log


esm_service_runner = ServiceRunner(
    service_name=EsmService.service_name,
    service_function=EsmService().run,
    period_hours=24,
)
