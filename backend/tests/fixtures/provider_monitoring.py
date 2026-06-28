"""Test data fixtures for the provider monitoring service."""

import pytest

from app import models
from tests.utils.create_data.provider_monitoring import (
    create_provider_monitoring_service_logs,
    create_provider_monitoring_service_errors,
)


@pytest.fixture
def test_provider_monitoring_service_logs(session) -> list[models.ProviderMonitoringServiceLog]:
    """Create test provider monitoring service logs"""
    return create_provider_monitoring_service_logs(session)


@pytest.fixture
def test_provider_monitoring_service_errors(
    session, test_provider_monitoring_service_logs
) -> list[models.ServiceError]:
    """Create test provider monitoring service errors"""
    return create_provider_monitoring_service_errors(session, test_provider_monitoring_service_logs)
