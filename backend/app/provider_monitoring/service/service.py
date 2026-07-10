"""Daily sync job: calls every fetch_* in this module and upserts the day-keyed results.
Each fetcher is run independently — one failure doesn't abort the others. Transient failures are
absorbed by the HTTP-level retries in request_with_retry, and the next daily run re-fetches the
full window anyway, so there is no cross-run retry here. Every failure is recorded as an Error so
admins can spot partial failures (a run's derived is_success only flips to False on a critical
error)."""

from contextlib import nullcontext

from sqlalchemy.orm import Session

from app.database import db_session
from app.provider_monitoring.anthropic.fetch import fetch_anthropic_daily_usage
from app.provider_monitoring.apify.fetch import fetch_apify_daily_usage, fetch_apify_balance
from app.provider_monitoring.brightdata.fetch import fetch_brightdata_daily_usage, fetch_brightdata_balance
from app.provider_monitoring.stripe.fetch import fetch_stripe_daily_income
from app.models import ProviderMonitoringServiceLog
from app.service.models import ServiceErrorLevel, record_error
from app.provider_monitoring.service.schemas import ProviderMonitoringServiceLogOut
from app.service.registry import register_service
from app.service.service import BaseService


class ProviderMonitoringService(BaseService[ProviderMonitoringServiceLog]):
    """Runs all fetchers in sequence and upserts each into its own daily-history table."""

    service_name = "provider_monitoring_service"

    def __init__(self):
        """Initialise the service"""

        BaseService.__init__(self, ProviderMonitoringServiceLog)
        self.external_services = {
            "anthropic": [fetch_anthropic_daily_usage],
            "stripe": [fetch_stripe_daily_income],
            "apify": [fetch_apify_balance, fetch_apify_daily_usage],
            "brightdata": [fetch_brightdata_daily_usage, fetch_brightdata_balance],
        }

    def run(self, db: Session | None = None) -> ProviderMonitoringServiceLog:
        """Fetch the different external services data
        :param db: optional session to run within; if omitted, one is created and closed for the run
        :return Service log entry"""

        with db_session() if db is None else nullcontext(db) as db:
            service_log = self.start_run(db)

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
                                provider_monitoring_service_log_id=service_log.id,
                            )
            except Exception as exc:
                message = "Critical error in provider monitoring workflow"
                self.logger.exception(message)
                record_error(
                    db=db,
                    exc=exc,
                    message=message,
                    level=ServiceErrorLevel.CRITICAL,
                    provider_monitoring_service_log_id=service_log.id,
                )
            service_log.set_run_duration()
            db.commit()
            db.refresh(service_log)
            self.logger.info(f"Finished {self.service_name} run")
            return service_log


register_service(
    ProviderMonitoringService.service_name,
    ProviderMonitoringService().run,
    display_name="Provider Monitoring",
    run_period_hours=24,
    log_model=ProviderMonitoringServiceLog,
    log_schema=ProviderMonitoringServiceLogOut,
)
