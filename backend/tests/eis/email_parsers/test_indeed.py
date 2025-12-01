"""Tests for Indeed job email parser."""

from app.eis.email_parsers.indeed import parse_indeed_job_email
from tests.eis.resources import INDEED_EMAIL_3, INDEED_EMAIL_4


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
