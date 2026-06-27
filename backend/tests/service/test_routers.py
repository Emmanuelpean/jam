"""Tests for app/service/routers/service.py and the generic service-log endpoints.

Both the log-file endpoint (`/services/{name}/logs`) and the latest-run endpoint
(`/service-logs/{service_name}/latest`) have their logic inlined into the route handlers, so they are
tested over HTTP. Date-range log listing is covered by the per-service endpoint tests (job scraping /
rating / monitoring) against the generic ``/service-logs/{service_name}/`` route."""

import os
import tempfile
from unittest.mock import patch

from starlette import status
from starlette.testclient import TestClient


# ----------------------------------------------- GET SERVICE LOGS (FILE) ----------------------------------------


class TestGetServiceLogs:
    def test_returns_empty_when_log_file_missing(self, admin_client) -> None:
        """Returns zero lines when the log file does not exist."""

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.utilities.logger.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                resp = admin_client.get("/services/nonexistent/logs")

        assert resp.status_code == status.HTTP_200_OK
        assert resp.json() == {"lines": [], "total_lines": 0}

    def test_returns_last_n_lines_of_small_file(self, admin_client) -> None:
        """Returns the correct tail lines from a file under 1 MB."""

        log_lines = [f"line {i}" for i in range(20)]
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "test_service.log"), "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines) + "\n")

            with patch("app.utilities.logger.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                resp = admin_client.get("/services/test_service/logs?lines=5")

        body = resp.json()
        assert body["total_lines"] == 20
        assert body["lines"] == log_lines[-5:]

    def test_returns_all_lines_when_fewer_than_requested(self, admin_client) -> None:
        """Returns all lines when the file has fewer lines than requested."""

        log_lines = ["alpha", "beta", "gamma"]
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "svc.log"), "w", encoding="utf-8") as f:
                f.write("\n".join(log_lines) + "\n")

            with patch("app.utilities.logger.settings") as mock_settings:
                mock_settings.log_directory = tmpdir
                resp = admin_client.get("/services/svc/logs?lines=100")

        body = resp.json()
        assert body["lines"] == log_lines
        assert body["total_lines"] == 3

    def test_rejects_out_of_range_lines(self, admin_client) -> None:
        """`lines` is validated as `ge=1, le=10000` by the Query declaration."""

        assert admin_client.get("/services/svc/logs?lines=0").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert admin_client.get("/services/svc/logs?lines=10001").status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        """Non-admin users receive 403."""

        assert regular_user_client.get("/services/svc/logs").status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        """Unauthenticated requests receive 401."""

        assert client.get("/services/svc/logs").status_code == status.HTTP_401_UNAUTHORIZED


# -------------------------------------------------- GET LATEST --------------------------------------------------


class TestLatestServiceLog:
    endpoint = "/service-logs/email_scraper_service/latest"

    def test_returns_most_recent_log(self, admin_client, test_job_scraping_service_logs) -> None:
        """Returns the single most-recent log entry for the service."""

        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_200_OK
        most_recent = max(test_job_scraping_service_logs, key=lambda l: l.run_datetime)
        assert resp.json()["id"] == most_recent.id

    def test_returns_404_when_no_logs(self, admin_client) -> None:
        """Returns 404 when the service has no log entries."""

        resp = admin_client.get(self.endpoint)
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert "No service logs found" in resp.json()["detail"]

    def test_unknown_service_404(self, admin_client) -> None:
        """An unknown service name returns 404."""

        assert admin_client.get("/service-logs/nope/latest").status_code == status.HTTP_404_NOT_FOUND

    def test_non_admin_forbidden(self, regular_user_client) -> None:
        """Non-admin users receive 403."""

        assert regular_user_client.get(self.endpoint).status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated(self, client: TestClient) -> None:
        """Unauthenticated requests receive 401."""

        assert client.get(self.endpoint).status_code == status.HTTP_401_UNAUTHORIZED
