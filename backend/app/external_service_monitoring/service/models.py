"""SqlAlchemy Service log model"""

from app.base_models import CommonBase
from app.database import Base
from app.service_runner.models import ServiceLog


class ExternalServiceMonitoringServiceLog(ServiceLog, CommonBase, Base):
    pass
