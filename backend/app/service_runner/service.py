import datetime as dt
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.database import get_db
from app.service_runner.models import ServiceLog
from app.utilities.logger import AppLogger

ServiceLogT = TypeVar("ServiceLogT", bound=ServiceLog)


class Service(Generic[ServiceLogT]):
    """Base class for services.

    Parameterise with the concrete service-log model so ``start_run`` (and ``self.service_log_table``)
    are typed to that model, e.g. ``class ScrapedJobRater(Service[JobRatingServiceLog])``."""

    service_name = "service_name"

    def __init__(self, service_log_table: type[ServiceLogT]) -> None:
        """Object constructor
        :param service_log_table: ServiceLog table"""

        self.service_log_table = service_log_table
        self.logger = AppLogger.create_service_logger(self.service_name, "INFO")

    def start_run(self, db: Session | None = None) -> tuple[ServiceLogT, Session]:
        """Start a new service run
        :param db: Database session
        :return: The created service log entry and the database session"""

        db = next(get_db()) if db is None else db
        start = dt.datetime.now(dt.timezone.utc)
        service_log = self.service_log_table(run_datetime=start)
        db.add(service_log)
        db.commit()
        db.refresh(service_log)
        self.logger.info(f"Starting {self.service_name} run")
        return service_log, db
