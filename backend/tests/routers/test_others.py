"""Tests for the /others and /config routers."""

from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.config import settings
from tests.base_test import BaseTest


class TestCurrencies(BaseTest):

    endpoint = "/others/currencies/"

    def test_get_currencies(self, client: TestClient) -> None:
        """Test that the currencies endpoint returns a non-empty list of dicts."""
        response = client.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(isinstance(item, dict) for item in data)

    def test_get_currencies_have_expected_keys(self, client: TestClient) -> None:
        """Test that each currency dict has the expected keys."""
        response = client.get(self.endpoint)
        data = response.json()
        for item in data:
            assert "code" in item
            assert "name" in item


class TestConfig(BaseTest):

    endpoint = "/config/"

    def test_get_config_success(self, client: TestClient) -> None:
        """Test that the config endpoint returns expected keys."""
        response = client.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert "scraper_email" in data
        assert "support_email" in data
        assert "platform_sender_emails" in data
        assert "min_password_length" in data
        assert "app_demo_username" in data
        assert "scrape_max_retry" in data

    def test_get_config_values(self, client: TestClient) -> None:
        """Test that config values match application settings."""
        response = client.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert data["scraper_email"] == settings.scraper_email_username
        assert data["support_email"] == settings.support_email
        assert data["min_password_length"] == settings.min_password_length
        assert data["scrape_max_retry"] == settings.scrape_max_retry

    def test_get_config_demo_username(self, client: TestClient) -> None:
        """Test that config returns the hard-coded demo address."""
        response = client.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert data["app_demo_username"] == settings.demo_user_email

    def test_get_config_platform_sender_emails_is_dict(self, client: TestClient) -> None:
        """Test that platform_sender_emails is a dict mapping email -> platform name."""
        response = client.get(self.endpoint)
        data = response.json()
        assert isinstance(data["platform_sender_emails"], dict)


class TestStatus(BaseTest):

    endpoint = "/config/status"

    def test_get_status_no_maintenance(self, client: TestClient) -> None:
        """Test that /config/status returns expected keys with no maintenance setting."""
        response = client.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert "maintenance_scheduled_at" in data
        assert "test_mode" in data
        assert data["maintenance_scheduled_at"] is None

    def test_get_status_test_mode(self, client: TestClient) -> None:
        """Test that test_mode value matches app settings."""
        response = client.get(self.endpoint)
        data = response.json()
        assert data["test_mode"] == settings.test_mode

    def test_get_status_with_maintenance_setting(self, client: TestClient, session: Session) -> None:
        """Test that maintenance_scheduled_at is returned when set in the database."""
        scheduled_at = "2099-01-01T00:00:00+00:00"
        self.create_setting(session, "maintenance_scheduled_at", scheduled_at)

        response = client.get(self.endpoint)
        assert response.status_code == 200
        data = response.json()
        assert data["maintenance_scheduled_at"] == scheduled_at
