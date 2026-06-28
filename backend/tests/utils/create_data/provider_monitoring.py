"""Functions for creating provider monitoring service test data."""

from app import models
from tests.utils.create_data.utils import create_db_entries, override_properties
from tests.utils.test_data import provider_monitoring


def create_provider_monitoring_service_logs(db) -> list[models.ProviderMonitoringServiceLog]:
    """Create sample provider monitoring service logs"""

    data = provider_monitoring.PROVIDER_MONITORING_SERVICE_LOG_DATA
    print(f"Creating {len(data)} Provider Monitoring Service Logs...")
    return create_db_entries(db, models.ProviderMonitoringServiceLog, data)


def create_provider_monitoring_service_errors(db, service_logs) -> list[models.ServiceError]:
    """Create sample provider monitoring errors as unified ServiceError rows linked to their run"""

    data = override_properties(
        provider_monitoring.PROVIDER_MONITORING_SERVICE_ERROR_DATA,
        ("provider_monitoring_service_log_id", service_logs),
    )
    print(f"Creating {len(data)} Provider Monitoring Service Errors...")
    return create_db_entries(db, models.ServiceError, data)
