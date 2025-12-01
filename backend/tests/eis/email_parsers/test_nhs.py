"""Tests for NHS email parser."""

from app.eis.email_parsers.nhs import parse_nhs_job_email
from tests.eis.resources import NHS_EMAIL_3, NHS_EMAIL_4


class TestParseIndeedJobEmail:

    def test_email_1(self) -> None:

        output = parse_nhs_job_email(NHS_EMAIL_3["body"])
        assert len(output) == len(NHS_EMAIL_3["parsed_output"])
        for out, exp in zip(output, NHS_EMAIL_3["parsed_output"]):
            assert out.model_dump() == exp.model_dump()

    def test_email_2(self) -> None:

        output = parse_nhs_job_email(NHS_EMAIL_4["body"])
        assert len(output) == len(NHS_EMAIL_4["parsed_output"])
        for out, exp in zip(output, NHS_EMAIL_4["parsed_output"]):
            assert out.model_dump() == exp.model_dump()
