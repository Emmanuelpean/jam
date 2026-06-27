"""SqlAlchemy models for the provider monitoring runner."""

from sqlalchemy.orm import relationship

from app.base_models import CommonBase
from app.database import Base
from app.service.models import ServiceLog


class ProviderMonitoringServiceLog(ServiceLog, CommonBase, Base):
    # Relationships
    service_errors = relationship(
        "ServiceError", back_populates="provider_monitoring_service_log", cascade="all, delete-orphan"
    )
