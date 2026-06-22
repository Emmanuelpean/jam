"""SqlAlchemy models for the external service monitoring runner."""

from sqlalchemy.orm import relationship

from app.base_models import CommonBase
from app.database import Base
from app.service_runner.models import ServiceLog


class ExternalServiceMonitoringServiceLog(ServiceLog, CommonBase, Base):
    # Relationships
    service_errors = relationship(
        "Error", back_populates="external_service_monitoring_service_log", cascade="all, delete-orphan"
    )
