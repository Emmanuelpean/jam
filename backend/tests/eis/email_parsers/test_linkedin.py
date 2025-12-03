"""Tests for LinkedIn job email parser."""

import pytest

from app.eis.email_parsers.linkedin import parse_linkedin_job_email
from tests.eis.resources import LINKEDIN_EMAIL_3, LINKEDIN_EMAIL_4, LINKEDIN_EMAIL_5_BODY


class TestParseIndeedJobEmail:

    def test_email_1(self) -> None:

        output = parse_linkedin_job_email(LINKEDIN_EMAIL_3["body"])
        assert len(output) == len(LINKEDIN_EMAIL_3["parsed_output"])
        for out, exp in zip(output, LINKEDIN_EMAIL_3["parsed_output"]):
            assert out.model_dump() == exp.model_dump()

    def test_email_2(self) -> None:

        output = parse_linkedin_job_email(LINKEDIN_EMAIL_4["body"])
        assert len(output) == len(LINKEDIN_EMAIL_4["parsed_output"])
        for out, exp in zip(output, LINKEDIN_EMAIL_4["parsed_output"]):
            assert out.model_dump() == exp.model_dump()

    def test_fail(self) -> None:

        with pytest.raises(TypeError):
            parse_linkedin_job_email(LINKEDIN_EMAIL_5_BODY)
