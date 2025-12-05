"""Tests for the VeganJobs email parser."""

from app.eis.email_parsers.veganjobs import parse_veganjobs_email, extract_alert_name
from tests.eis.resources import VEGANJOBS_EMAIL_2, VEGANJOBS_EMAIL_3


class TestParseIndeedJobEmail:

    def test_email_1(self) -> None:

        output = parse_veganjobs_email(VEGANJOBS_EMAIL_2["body"])
        assert len(output) == len(VEGANJOBS_EMAIL_2["parsed_output"])
        for out, exp in zip(output, VEGANJOBS_EMAIL_2["parsed_output"]):
            assert out.model_dump() == exp.model_dump()

    def test_email_2(self) -> None:

        output = parse_veganjobs_email(VEGANJOBS_EMAIL_3["body"])
        assert len(output) == len(VEGANJOBS_EMAIL_3["parsed_output"])
        for out, exp in zip(output, VEGANJOBS_EMAIL_3["parsed_output"]):
            assert out.model_dump() == exp.model_dump()


class TestExtractAlertTitle(object):
    """Test suite for extract_alert_title function."""

    def test_extract_alert_title(self) -> None:
        """Test extraction of job titles from VeganJobs email body."""

        assert extract_alert_name('Job Alert Results Matching "Jobs"') == "Jobs"
