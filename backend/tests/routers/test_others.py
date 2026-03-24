"""Tests for the /others and /config routers."""

from app.config import settings
from app.core.models import Setting


class TestCurrencies:

    def test_get_currencies(self, client) -> None:
        """Test that the currencies endpoint returns a non-empty list of dicts."""
        response = client.get("/others/currencies/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(isinstance(item, dict) for item in data)

    def test_get_currencies_have_expected_keys(self, client) -> None:
        """Test that each currency dict has the expected keys."""
        response = client.get("/others/currencies/")
        data = response.json()
        for item in data:
            assert "code" in item
            assert "name" in item


class TestCountries:

    def test_get_countries(self, client) -> None:
        """Test that the countries endpoint returns a non-empty list of dicts."""
        response = client.get("/others/countries/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(isinstance(item, dict) for item in data)

    def test_get_countries_have_expected_keys(self, client) -> None:
        """Test that each country dict has the expected keys."""
        response = client.get("/others/countries/")
        data = response.json()
        for item in data:
            assert "code" in item
            assert "name" in item


class TestConfig:

    def test_get_config_success(self, client, test_demo_user) -> None:
        """Test that the config endpoint returns expected keys."""
        response = client.get("/config/")
        assert response.status_code == 200
        data = response.json()
        assert "scraper_email" in data
        assert "support_email" in data
        assert "platform_sender_emails" in data
        assert "min_password_length" in data
        assert "app_demo_username" in data
        assert "scrape_max_retry" in data

    def test_get_config_values(self, client, test_demo_user) -> None:
        """Test that config values match application settings."""
        response = client.get("/config/")
        assert response.status_code == 200
        data = response.json()
        assert data["scraper_email"] == settings.scraper_email_username
        assert data["support_email"] == settings.support_email
        assert data["min_password_length"] == settings.min_password_length
        assert data["scrape_max_retry"] == settings.scrape_max_retry

    def test_get_config_demo_username(self, client, test_demo_user) -> None:
        """Test that config returns the demo user's email."""
        response = client.get("/config/")
        assert response.status_code == 200
        data = response.json()
        assert data["app_demo_username"] == test_demo_user.email

    def test_get_config_platform_sender_emails_is_dict(self, client, test_demo_user) -> None:
        """Test that platform_sender_emails is a dict mapping email -> platform name."""
        response = client.get("/config/")
        data = response.json()
        assert isinstance(data["platform_sender_emails"], dict)


class TestStatus:

    def test_get_status_no_maintenance(self, client) -> None:
        """Test that /config/status returns expected keys with no maintenance setting."""
        response = client.get("/config/status")
        assert response.status_code == 200
        data = response.json()
        assert "maintenance_scheduled_at" in data
        assert "test_mode" in data
        assert data["maintenance_scheduled_at"] is None

    def test_get_status_test_mode(self, client) -> None:
        """Test that test_mode value matches app settings."""
        response = client.get("/config/status")
        data = response.json()
        assert data["test_mode"] == settings.test_mode

    def test_get_status_with_maintenance_setting(self, client, session) -> None:
        """Test that maintenance_scheduled_at is returned when set in the database."""
        scheduled_at = "2099-01-01T00:00:00+00:00"
        setting = Setting(name="maintenance_scheduled_at", value=scheduled_at)
        session.add(setting)
        session.commit()

        response = client.get("/config/status")
        assert response.status_code == 200
        data = response.json()
        assert data["maintenance_scheduled_at"] == scheduled_at
