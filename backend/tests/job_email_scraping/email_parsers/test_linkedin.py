"""Tests for LinkedIn job email parser."""

import pytest

from app.job_email_scraping.email_parsers.linkedin import parse_linkedin_job_email, extract_alert_name
from utils.job_email_resources import (
    LINKEDIN_EMAIL_3,
    LINKEDIN_EMAIL_4,
    LINKEDIN_EMAIL_5,
    LINKEDIN_EMAIL_6,
    LINKEDIN_EMAIL_7,
    LINKEDIN_EMAIL_MALFORMED_BODY,
)


class TestParseIndeedJobEmail:

    @pytest.mark.parametrize(
        "email", [LINKEDIN_EMAIL_3, LINKEDIN_EMAIL_4, LINKEDIN_EMAIL_5, LINKEDIN_EMAIL_6, LINKEDIN_EMAIL_7]
    )
    def test_email(self, email: dict) -> None:

        output = parse_linkedin_job_email(email["body"])
        assert len(output) == len(email["parsed_output"])
        for out, exp in zip(output, email["parsed_output"]):
            assert out.model_dump() == exp.model_dump()

    def test_fail(self) -> None:

        with pytest.raises(TypeError):
            parse_linkedin_job_email(LINKEDIN_EMAIL_MALFORMED_BODY)


class TestExtractLinkedInJobTitle:
    """Test suite for extract_linkedin_job_title function."""

    @pytest.mark.parametrize(
        "alert_string,expected_title",
        [
            # Basic LinkedIn alert format
            ("“test & development”: TrueNorth® - Software Engineer in Test and more", "test & development"),
            ("“lab automation”: Hyper Recruitment Solutions - Automation Technician and more", "lab automation"),
            # Various job categories
            ("“software engineer”: Google - Senior Software Engineer and more", "software engineer"),
            ("“data science”: Meta - Machine Learning Researcher and more", "data science"),
            ("“R&D”: Pfizer - R&D Scientist and more", "R&D"),
            ("“UI/UX design”: Apple - UI/UX Designer and more", "UI/UX design"),
            # Edge cases with special characters in quotes
            ("“python/java developer”: Company - Developer and more", "python/java developer"),
            ("“machine learning & AI”: OpenAI - ML Engineer and more", "machine learning & AI"),
        ],
    )
    def test_extract_valid_linkedin_titles(self, alert_string: str, expected_title: str) -> None:
        """Test extraction of job titles from valid LinkedIn alert strings."""
        result = extract_alert_name(alert_string)
        assert result == expected_title

    @pytest.mark.parametrize(
        "alert_string",
        [
            # No matching pattern
            "Check out these new job opportunities",
            "Your weekly job digest",
            "",
            # Missing quotes
            "category: Company - Job Title and more",
            "Software Engineer and more",
        ],
    )
    def test_extract_no_match(self, alert_string: str) -> None:
        """Test that None is returned when no pattern matches."""
        result = extract_alert_name(alert_string)
        assert result is None

    def test_whitespace_handling(self) -> None:
        """Test that extra whitespace inside quotes is properly stripped."""
        result = extract_alert_name("“  data scientist  ”: Company - Role and more")
        assert result == "data scientist"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_empty_quotes(self) -> None:
        """Test handling of empty quotes."""
        result = extract_alert_name("“”: Company - Job Title and more")
        assert result is None

    def test_multiple_quotes_first_match(self) -> None:
        """Test that only the first quoted string is extracted."""
        result = extract_alert_name("“first”: Company “second” - Role and more")
        assert result == "first"

    @pytest.mark.parametrize(
        "alert_string,expected_title",
        [
            # Single word categories
            ("“python”: Company - Developer and more", "python"),
            ("“engineering”: Company - Engineer and more", "engineering"),
            # Multi-word with various separators
            ("“full-stack developer”: Company - Role and more", "full-stack developer"),
            ("“senior level”: Company - Role and more", "senior level"),
        ],
    )
    def test_various_title_formats(self, alert_string: str, expected_title: str) -> None:
        """Test extraction with different title formats."""
        result = extract_alert_name(alert_string)
        assert result == expected_title
