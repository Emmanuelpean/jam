"""Tests for Indeed job email parser."""

import pytest

from app.job_email_scraping.email_parsers.indeed import parse_indeed_job_email, extract_alert_name
from tests.job_email_scraping.resources import INDEED_EMAIL_3, INDEED_EMAIL_4


class TestParseIndeedJobEmail:

    def test_email_1(self) -> None:

        output = parse_indeed_job_email(INDEED_EMAIL_3["body"])
        assert len(output) == len(INDEED_EMAIL_3["parsed_output"])
        for out, exp in zip(output, INDEED_EMAIL_3["parsed_output"]):
            assert out.model_dump() == exp.model_dump()

    def test_email_2(self) -> None:

        output = parse_indeed_job_email(INDEED_EMAIL_4["body"])
        assert len(output) == len(INDEED_EMAIL_4["parsed_output"])
        for out, exp in zip(output, INDEED_EMAIL_4["parsed_output"]):
            assert out.model_dump() == exp.model_dump()


class TestParseEmailName:
    """Test suite for extract_job_title function."""

    @pytest.mark.parametrize(
        "alert_string,expected_title",
        [
            # Pattern: "X more [job title] job"
            (
                "Principal Optical Scientist/Engineer at QinetiQ and 1 more optical engineer job for you!",
                "optical engineer",
            ),
            ("1 new optical engineer job", "optical engineer"),
            # Pattern: "hiring for [job title] + X new"
            (
                "Yoti is hiring for Junior Research and Development Engineer + 30 new R&D Development Engineer jobs",
                "R&D Development Engineer",
            ),
            # Additional test cases
            ("5 more Software Engineer jobs available", "Software Engineer"),
            ("Company is hiring for Data Scientist + 10 new positions", None),
            ("2 new Machine Learning Engineer jobs", "Machine Learning Engineer"),
            ("15 more Senior Full-Stack Developer jobs for you", "Senior Full-Stack Developer"),
            # Job titles with special characters
            ("3 more R&D Engineer jobs posted today", "R&D Engineer"),
            ("10 new DevOps/Cloud Engineer jobs", "DevOps/Cloud Engineer"),
            ("Hiring for UI/UX Designer + 5 new openings", None),
        ],
    )
    def test_extract_valid_job_titles(self, alert_string: str, expected_title: str) -> None:
        """Test extraction of job titles from valid alert strings."""
        result = extract_alert_name(alert_string)
        assert result == expected_title

    @pytest.mark.parametrize(
        "alert_string",
        [
            # No matching pattern
            "Check out these amazing opportunities!",
            "New positions available at top companies",
            "Your job search update",
            "",
            # Missing key components
            "optical engineer",
            "1 more job",
            "hiring for a position",
        ],
    )
    def test_extract_no_match(self, alert_string: str) -> None:
        """Test that None is returned when no pattern matches."""
        result = extract_alert_name(alert_string)
        assert result is None

    def test_singular_vs_plural_job(self) -> None:
        """Test handling of both 'job' and 'jobs'."""
        singular = extract_alert_name("1 new Software Engineer job")
        plural = extract_alert_name("5 new Software Engineer jobs")

        assert singular == "Software Engineer"
        assert plural == "Software Engineer"

    def test_whitespace_handling(self) -> None:
        """Test that extra whitespace is properly stripped."""
        result = extract_alert_name("3 more   Data Scientist   jobs")
        assert result == "Data Scientist"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    @pytest.mark.parametrize(
        "alert_string,expected_title",
        [
            # Test different number formats
            ("1 more optical engineer job", "optical engineer"),
            ("10 new optical engineer jobs", "optical engineer"),
            ("100 more optical engineer jobs", "optical engineer"),
        ],
    )
    def test_various_job_counts(self, alert_string: str, expected_title: str) -> None:
        """Test extraction with different job count numbers."""
        result = extract_alert_name(alert_string)
        assert result == expected_title
