"""Unit tests for email_parser module methods"""

import pytest

from app.eis.email_parser import (
    extract_indeed_job_ids,
    extract_linkedin_job_ids,
    extract_veganjobs_job_ids,
    extract_nhs_job_ids,
)
from tests.eis import resources


# ------------------------------------------------------ LINKEDIN ------------------------------------------------------


class TestExtractLinkedinJobIds:
    """Test class for extract_linkedin_job_ids method"""

    def test_extract_linkedin_job_ids_real_email(self) -> None:
        """Test extracting LinkedIn job IDs from real LinkedIn email content"""

        job_ids = extract_linkedin_job_ids(resources.LINKEDIN_EMAIL_1_BODY)
        assert job_ids == resources.LINKEDIN_JOB_IDS_1

    def test_extract_linkedin_job_ids_empty_body(self) -> None:
        """Test extracting job IDs from empty body"""

        job_ids = extract_linkedin_job_ids("")
        assert job_ids == []

    def test_extract_linkedin_job_ids_no_jobs(self) -> None:
        """Test extracting job IDs from body with no LinkedIn job URLs"""

        body = """
        This is a test email with no LinkedIn job URLs.
        It contains some other URLs like:
        - https://www.google.com
        - https://www.example.com
        - https://www.linkedin.com/profile/some-user
        But no job view URLs.
        """

        job_ids = extract_linkedin_job_ids(body)
        assert job_ids == []

    @pytest.mark.parametrize(
        "url_pattern,expected_id",
        [
            ("https://www.linkedin.com/jobs/view/1234567890", "1234567890"),
            ("https://www.linkedin.com/comm/jobs/view/9876543210", "9876543210"),
            ("HTTPS://WWW.LINKEDIN.COM/JOBS/VIEW/5555555555", "5555555555"),
            ("https://linkedin.com/jobs/view/1111111111", "1111111111"),
            ("http://www.linkedin.com/jobs/view/2222222222", "2222222222"),
        ],
    )
    def test_extract_linkedin_job_ids_url_variations(self, url_pattern, expected_id) -> None:
        """Test extracting job IDs from various URL patterns"""

        body = f"Check out this job: {url_pattern}"

        job_ids = extract_linkedin_job_ids(body)
        assert job_ids == [expected_id]

    def test_extract_linkedin_job_ids_with_duplicate_ids(self) -> None:
        """Test that duplicate job IDs are removed"""

        body = """
        Job 1: https://www.linkedin.com/jobs/view/1111111111
        Job 2: https://www.linkedin.com/jobs/view/2222222222  
        Job 3: https://www.linkedin.com/jobs/view/1111111111
        Job 4: https://www.linkedin.com/jobs/view/3333333333
        Job 5: https://www.linkedin.com/jobs/view/2222222222
        """

        job_ids = extract_linkedin_job_ids(body)
        assert job_ids == ["1111111111", "2222222222", "3333333333"]

    def test_extract_linkedin_job_ids_with_query_parameters(self) -> None:
        """Test extracting job IDs from URLs with query parameters (like the real email)"""

        body = """
        View job: https://www.linkedin.com/comm/jobs/view/4289870503/?trackingId=tt9C%2FzqOXzxRyy9uU5vDOw%3D%3D&refId=something
        Another job: https://www.linkedin.com/jobs/view/1234567890?ref=email&source=alert
        """

        job_ids = extract_linkedin_job_ids(body)
        assert job_ids == ["4289870503", "1234567890"]

    def test_extract_linkedin_job_ids_malformed_urls(self) -> None:
        """Test that malformed LinkedIn URLs are ignored"""

        body = """
        Good URL: https://www.linkedin.com/jobs/view/1111111111
        Malformed: https://www.linkedin.com/jobs/view/
        Malformed: https://www.linkedin.com/jobs/view/abcd
        Another good: https://www.linkedin.com/jobs/view/2222222222
        """

        job_ids = extract_linkedin_job_ids(body)
        assert job_ids == ["1111111111", "2222222222"]


# ------------------------------------------------------- INDEED -------------------------------------------------------


class TestExtractIndeedJobIds:
    """Test class for extract_indeed_job_ids method"""

    def test_extract_indeed_job_ids_real_email(self) -> None:
        """Test extracting Indeed job IDs from real Indeed email content"""

        job_ids = extract_indeed_job_ids(resources.INDEED_EMAIL_1_BODY)
        assert job_ids == resources.INDEED_JOB_IDS_1

    def test_extract_indeed_job_ids_empty_body(self) -> None:
        """Test extracting job IDs from empty body"""

        job_ids = extract_indeed_job_ids("")
        assert job_ids == []

    def test_extract_indeed_job_ids_no_jobs(self) -> None:
        """Test extracting job IDs from body with no Indeed job URLs"""

        body = """
        This is a test email with no Indeed job URLs.
        It contains some other URLs like:
        - https://www.google.com
        - https://www.example.com
        - https://www.indeed.com/profile/some-user
        But no job view URLs.
        """

        job_ids = extract_indeed_job_ids(body)
        assert job_ids == []

    @pytest.mark.parametrize(
        "url_pattern,expected_id",
        [
            ("https://uk.indeed.com/rc/clk/dl?jk=1234567890abcdef&from=ja", "1234567890abcdef"),
            ("HTTPS://UK.INDEED.COM/RC/CLK/DL?JK=5555555555AAAA&FROM=JA", "5555555555AAAA"),
            ("http://indeed.com/rc/clk/dl?jk=1111111111bbbb&other=param", "1111111111bbbb"),
        ],
    )
    def test_extract_indeed_job_ids_url_variations(self, url_pattern, expected_id) -> None:
        """Test extracting job IDs from various URL patterns"""

        body = f"Check out this job: {url_pattern}"

        job_ids = extract_indeed_job_ids(body)

        assert len(job_ids) == 1
        assert job_ids[0] == expected_id

    def test_extract_indeed_job_ids_with_duplicate_ids(self) -> None:
        """Test that duplicate job IDs are removed"""

        body = """
        Job 1: https://uk.indeed.com/rc/clk/dl?jk=1111111111aaa&from=ja
        Job 2: https://uk.indeed.com/rc/clk/dl?jk=2222222222bbb&from=ja
        Job 3: https://uk.indeed.com/rc/clk/dl?jk=1111111111aaa&from=ja
        Job 4: https://uk.indeed.com/rc/clk/dl?jk=3333333333ccc&from=ja
        Job 5: https://uk.indeed.com/rc/clk/dl?jk=2222222222bbb&from=ja
        """

        job_ids = extract_indeed_job_ids(body)

        assert len(job_ids) == 3
        assert job_ids == ["1111111111aaa", "2222222222bbb", "3333333333ccc"]

    def test_extract_indeed_job_ids_malformed_urls(self) -> None:
        """Test that malformed Indeed URLs are ignored"""

        body = """
        Good URL: https://uk.indeed.com/rc/clk/dl?jk=1111111111aaa&from=ja
        Malformed: https://uk.indeed.com/rc/clk/dl?from=ja
        Malformed: https://uk.indeed.com/rc/clk/dl?jk=
        Another good: https://uk.indeed.com/rc/clk/dl?jk=2222222222bbb&from=ja
        """

        job_ids = extract_indeed_job_ids(body)

        assert len(job_ids) == 2
        assert job_ids == ["1111111111aaa", "2222222222bbb"]


# ------------------------------------------------------ VEGANJOBS -----------------------------------------------------


class TestExtractVeganJobsJobIds:
    """Test class for extract_veganjobs_job_ids method"""

    def test_extract_job_ids_real_email(self) -> None:
        """Test extracting LinkedIn job IDs from real LinkedIn email content"""

        job_ids = extract_veganjobs_job_ids(resources.VEGANJOBS_EMAIL_1_BODY)
        assert job_ids == resources.VEGANJOBS_JOB_IDS_1

    def test_extract_job_ids_empty_body(self) -> None:
        """Test extracting job IDs from empty body"""

        job_ids = extract_veganjobs_job_ids("")
        assert job_ids == []

    def test_extract_job_ids_no_jobs(self) -> None:
        """Test extracting job IDs from body with no LinkedIn job URLs"""

        body = """
        This is a test email with no LinkedIn job URLs.
        It contains some other URLs like:
        - https://www.google.com
        - https://www.example.com
        - https://www.linkedin.com/profile/some-user
        But no job view URLs.
        """

        job_ids = extract_veganjobs_job_ids(body)
        assert job_ids == []

    def test_extract_job_ids_with_duplicate_ids(self) -> None:
        """Test that duplicate job IDs are removed"""

        body = """
        Job 1: https://veganjobs.com/job/1111111111
        Job 2: https://veganjobs.com/job/2222222222  
        Job 3: https://veganjobs.com/job/1111111111
        Job 4: https://veganjobs.com/job/3333333333
        Job 5: https://veganjobs.com/job/2222222222
        """

        job_ids = extract_veganjobs_job_ids(body)

        assert len(job_ids) == 3
        assert job_ids == ["1111111111", "2222222222", "3333333333"]


# --------------------------------------------------------- NHS --------------------------------------------------------


class TestExtractNhsJobIds:
    """Test class for extract_nhs_job_ids method"""

    def test_extract_nhs_job_ids_real_email(self) -> None:
        """Test extracting Indeed job IDs from real Indeed email content"""

        job_ids = extract_nhs_job_ids(resources.NHS_EMAIL_1_BODY)
        assert job_ids == resources.NHS_JOB_IDS_1

    def test_extract_nhs_job_ids_empty_body(self) -> None:
        """Test extracting job IDs from empty body"""

        job_ids = extract_nhs_job_ids("")
        assert job_ids == []

    def test_extract_nhs_job_ids_no_jobs(self) -> None:
        """Test extracting job IDs from body with no Indeed job URLs"""

        body = """
        This is a test email with no Indeed job URLs.
        It contains some other URLs like:
        - https://www.google.com
        - https://www.example.com
        - https://www.indeed.com/profile/some-user
        But no job view URLs.
        """

        job_ids = extract_nhs_job_ids(body)
        assert job_ids == []

    def test_extract_nhs_job_ids_with_duplicate_ids(self) -> None:
        """Test that duplicate job IDs are removed"""

        body = """
        Job 1: https://beta.jobs.nhs.uk/candidate/jobadvert/1111111111aaa
        Job 2: https://beta.jobs.nhs.uk/candidate/jobadvert/2222222222bbb
        Job 3: https://beta.jobs.nhs.uk/candidate/jobadvert/1111111111aaa
        Job 4: https://beta.jobs.nhs.uk/candidate/jobadvert/3333333333ccc
        Job 5: https://beta.jobs.nhs.uk/candidate/jobadvert/2222222222bbb
        """

        job_ids = extract_nhs_job_ids(body)

        assert len(job_ids) == 3
        assert job_ids == ["1111111111aaa", "2222222222bbb", "3333333333ccc"]
