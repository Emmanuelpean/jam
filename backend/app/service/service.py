from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from app.service.models import ServiceLog
from app.utilities.logger import AppLogger

ServiceLogT = TypeVar("ServiceLogT", bound=ServiceLog)


class BaseService(Generic[ServiceLogT]):
    """Base class for services"""

    service_name = "service_name"

    def __init__(self, service_log_table: type[ServiceLogT]) -> None:
        """Object constructor
        :param service_log_table: ServiceLog table"""

        self.service_log_table = service_log_table
        self.logger = AppLogger.create_service_logger(self.service_name, "INFO")

    def start_run(self, db: Session) -> ServiceLogT:
        """Create and persist the service-log row for a new run.
        The caller owns the session (typically via with db_session() as db) and passes it in.
        :param db: Database session
        :return: The created service log entry"""

        service_log = self.service_log_table()
        db.add(service_log)
        db.commit()
        db.refresh(service_log)
        self.logger.info(f"Starting {self.service_name} run")
        return service_log
