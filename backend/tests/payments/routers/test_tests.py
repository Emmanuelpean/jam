"""Tests for payment testing endpoints."""

from unittest.mock import patch

from fastapi import status
from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestPaymentTestRouterRequiresTestMode:
    """Tests that all payment test router endpoints return 403 when test_mode is disabled."""

    @patch("app.routers.utility.settings.test_mode", False)
    def test_delete_all_customers_returns_403(self) -> None:
        response = client.delete("/test/payments/delete-all-customers")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]

    @patch("app.routers.utility.settings.test_mode", False)
    def test_advance_test_clock_returns_403(self) -> None:
        response = client.post("/test/payments/advance-test-clock", json={"days": 1})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Test mode not enabled" in response.json()["detail"]
