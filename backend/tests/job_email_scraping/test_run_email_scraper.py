"""Tests for run_email_scraper CLI script."""

from unittest.mock import patch, MagicMock

import pytest

from app.job_email_scraping.run_email_scraper import main


class TestRunEmailScraperMain:
    """Tests for the run_email_scraper main function."""

    @patch("app.job_email_scraping.run_email_scraper.JobEmailScraper")
    def test_default_days(self, mock_scraper_cls, capsys) -> None:
        """Runs scraper with default days=1 and prints Done."""

        mock_scraper_cls.return_value.run_scraping.return_value = MagicMock(error_message=None)

        with patch("sys.argv", ["run_email_scraper"]):
            main()

        mock_scraper_cls.return_value.run_scraping.assert_called_once_with(timedelta_days=1)
        assert "Done!" in capsys.readouterr().out

    @patch("app.job_email_scraping.run_email_scraper.JobEmailScraper")
    def test_custom_days(self, mock_scraper_cls) -> None:
        """Passes --days 3.5 through to run_scraping."""

        mock_scraper_cls.return_value.run_scraping.return_value = MagicMock(error_message=None)

        with patch("sys.argv", ["run_email_scraper", "--days", "3.5"]):
            main()

        mock_scraper_cls.return_value.run_scraping.assert_called_once_with(timedelta_days=3.5)

    @patch("app.job_email_scraping.run_email_scraper.JobEmailScraper")
    def test_short_flag_days(self, mock_scraper_cls) -> None:
        """Short -d flag works the same as --days."""

        mock_scraper_cls.return_value.run_scraping.return_value = MagicMock(error_message=None)

        with patch("sys.argv", ["run_email_scraper", "-d", "2"]):
            main()

        mock_scraper_cls.return_value.run_scraping.assert_called_once_with(timedelta_days=2.0)

    @patch("app.job_email_scraping.run_email_scraper.JobEmailScraper")
    def test_negative_days_exits(self, mock_scraper_cls, capsys) -> None:
        """Negative days prints error and exits with code 1 without running scraper."""

        with patch("sys.argv", ["run_email_scraper", "--days", "-1"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        error = exc_info.value
        assert isinstance(error, SystemExit)
        assert error.code == 1
        assert "days must be a positive number" in capsys.readouterr().out
        mock_scraper_cls.assert_not_called()

    @patch("app.job_email_scraping.run_email_scraper.JobEmailScraper")
    def test_zero_days_exits(self, mock_scraper_cls, capsys) -> None:
        """Zero days prints error and exits with code 1 without running scraper."""

        with patch("sys.argv", ["run_email_scraper", "--days", "0"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        error = exc_info.value
        assert isinstance(error, SystemExit)
        assert error.code == 1
        assert "days must be a positive number" in capsys.readouterr().out
        mock_scraper_cls.assert_not_called()

    @patch("app.job_email_scraping.run_email_scraper.JobEmailScraper")
    def test_scraping_error_exits(self, mock_scraper_cls, capsys) -> None:
        """Error in scraping result prints error message and exits with code 1."""

        mock_scraper_cls.return_value.run_scraping.return_value = MagicMock(error_message="Connection timeout")

        with patch("sys.argv", ["run_email_scraper"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

        error = exc_info.value
        assert isinstance(error, SystemExit)
        assert error.code == 1
        assert "Connection timeout" in capsys.readouterr().out
