"""Tests for job email scraping filtering logic."""

import uuid

import pytest

from app.job_email_scraping.filtering import (
    apply_rule_to_values,
    is_job_filtered_out,
    job_matches_rule_python,
    rule_to_sql_predicate,
)
from app.models import ScrapedJob, ScrapingExclusionFilter


class TestApplyRuleToValues:
    @pytest.mark.parametrize(
        "value,rule_val,op,case_sensitive,expected",
        [
            # contains / not_contains
            ("Senior Python Developer", "Python", "contains", False, True),
            ("Senior python Developer", "Python", "contains", False, True),
            ("Senior python Developer", "Python", "contains", True, False),
            ("Backend Developer", "Python", "contains", False, False),
            ("CloudTech Solutions", "Tech", "not_contains", False, False),
            ("FinCorp Ltd", "Tech", "not_contains", False, True),
            # equals / not_equals (string)
            ("StartupXYZ", "StartupXYZ", "equals", False, True),
            ("startupxyz", "StartupXYZ", "equals", True, False),
            ("StartupXYZ", "OtherCo", "not_equals", False, True),
            ("StartupXYZ", "StartupXYZ", "not_equals", False, False),
            # starts_with / ends_with
            ("Machine Learning Engineer", "Machine", "starts_with", False, True),
            ("machine Learning Engineer", "Machine", "starts_with", True, False),
            ("Full Stack Engineer", "Engineer", "ends_with", False, True),
            ("Full Stack engineer", "Engineer", "ends_with", True, False),
            # numeric less_than / greater_than
            (90000, "100000", "less_than", False, True),
            (120000, "100000", "less_than", False, False),
            (95000, "90000", "greater_than", False, True),
            ("85000", "90000", "greater_than", False, False),
            # None / invalid numeric
            ("not-a-number", "100000", "less_than", False, False),
        ],
    )
    def test_apply_rule_to_values(self, value, rule_val, op, case_sensitive, expected) -> None:
        """Test various combinations of values, rule values, operators, and case sensitivity."""

        result = apply_rule_to_values(job_value=value, rule_value=rule_val, op=op, case_sensitive=case_sensitive)
        assert result is expected


class TestRuleToSqlPredicate:

    @staticmethod
    def create_filter(session, **kwargs) -> ScrapingExclusionFilter:
        """Helper to create and persist a ScrapingFilter."""

        rule = ScrapingExclusionFilter(owner_id=1, **kwargs)
        session.add(rule)
        session.commit()
        return rule

    def test_contains_case_insensitive(self, test_users, session) -> None:
        # Simulate ScrapedJob.title column with a SQLAlchemy column()

        rule = self.create_filter(session, type="title", operator="contains", value="python", case_sensitive=False)
        predicate = rule_to_sql_predicate(rule)

        # Ensure predicate is a SQL expression and uses ILIKE/LOWER semantics via contains
        expected = "lower(scraped_job.title) IS NOT NULL AND (lower(scraped_job.title) LIKE '%' || :lower_1 || '%')"
        assert str(predicate) == expected

    def test_equals_numeric_salary(self, test_users, session) -> None:
        """Test numeric equality operator compiles correctly."""

        rule = self.create_filter(
            session, type="salary_min", operator="less_than", value="100000", case_sensitive=False
        )
        predicate = rule_to_sql_predicate(rule)
        assert str(predicate) == "scraped_job.salary_min IS NOT NULL AND scraped_job.salary_min < :salary_min_1"


class TestJobMatchesRulePython:

    @pytest.mark.parametrize(
        "title,value,op,case_sensitive,expected",
        [
            ("Senior Python Developer", "python", "contains", False, True),
            ("Senior Python Developer", "python", "contains", True, False),
            ("Java Developer", "python", "contains", False, False),
            ("Java Developer", "python", "not_contains", False, True),
            ("Python Developer", "Python Developer", "equals", False, True),
            ("python developer", "Python Developer", "equals", True, False),
            ("Python Developer", "Java", "not_equals", False, True),
            ("Python Developer", "python", "starts_with", False, True),
            ("Python Developer", "Developer", "ends_with", False, True),
        ],
    )
    def test_string_operators(self, title, value, op, case_sensitive, expected) -> None:
        job = ScrapedJob(title=title)
        rule = ScrapingExclusionFilter(type="title", operator=op, value=value, case_sensitive=case_sensitive)
        assert job_matches_rule_python(job, rule) is expected

    @pytest.mark.parametrize(
        "salary,value,op,expected",
        [
            (50000, "60000", "less_than", True),
            (70000, "60000", "less_than", False),
            (70000, "60000", "greater_than", True),
            (50000, "60000", "greater_than", False),
        ],
    )
    def test_numeric_operators(self, salary, value, op, expected) -> None:
        job = ScrapedJob(salary_min=salary)
        rule = ScrapingExclusionFilter(type="salary_min", operator=op, value=value, case_sensitive=False)
        assert job_matches_rule_python(job, rule) is expected

    def test_field_none_returns_false(self) -> None:
        job = ScrapedJob(title=None)
        rule = ScrapingExclusionFilter(type="title", operator="contains", value="python", case_sensitive=False)
        assert job_matches_rule_python(job, rule) is False

    def test_missing_field_returns_false(self) -> None:
        job = ScrapedJob()
        rule = ScrapingExclusionFilter(type="title", operator="contains", value="python", case_sensitive=False)
        assert job_matches_rule_python(job, rule) is False


class TestIsJobFilteredOut:

    @staticmethod
    def _make_scraped_job(session, owner_id, service_log_id, **kwargs) -> ScrapedJob:
        defaults = dict(
            external_job_id=str(uuid.uuid4()), platform="linkedin", title="Python Developer", company="Acme"
        )
        defaults.update(kwargs)
        job = ScrapedJob(owner_id=owner_id, service_log_id=service_log_id, **defaults)
        session.add(job)
        session.commit()
        session.refresh(job)
        return job

    @staticmethod
    def _make_scraping_filter(session, owner_id, **kwargs) -> ScrapingExclusionFilter:
        defaults = dict(is_active=True)
        defaults.update(kwargs)
        f = ScrapingExclusionFilter(owner_id=owner_id, **defaults)
        session.add(f)
        session.commit()
        session.refresh(f)
        return f

    def test_matching_rule_returns_filter(self, session, test_users, test_job_scraping_service_log) -> None:
        job = self._make_scraped_job(
            session, test_users[0].id, test_job_scraping_service_log.id, title="Python Developer"
        )
        rule = self._make_scraping_filter(
            session, test_users[0].id, type="title", operator="contains", value="python", case_sensitive=False
        )
        result = is_job_filtered_out(session, job)
        assert result is not None
        assert result.id == rule.id

    def test_no_matching_rule_returns_none(self, session, test_users, test_job_scraping_service_log) -> None:
        job = self._make_scraped_job(
            session, test_users[0].id, test_job_scraping_service_log.id, title="Java Developer"
        )
        self._make_scraping_filter(
            session, test_users[0].id, type="title", operator="contains", value="python", case_sensitive=False
        )
        assert is_job_filtered_out(session, job) is None

    def test_inactive_rule_is_ignored(self, session, test_users, test_job_scraping_service_log) -> None:
        job = self._make_scraped_job(
            session, test_users[0].id, test_job_scraping_service_log.id, title="Python Developer"
        )
        self._make_scraping_filter(
            session,
            test_users[0].id,
            type="title",
            operator="contains",
            value="python",
            case_sensitive=False,
            is_active=False,
        )
        assert is_job_filtered_out(session, job) is None

    def test_rule_from_other_owner_is_ignored(self, session, test_users, test_job_scraping_service_log) -> None:
        job = self._make_scraped_job(
            session, test_users[0].id, test_job_scraping_service_log.id, title="Python Developer"
        )
        self._make_scraping_filter(
            session, test_users[1].id, type="title", operator="contains", value="python", case_sensitive=False
        )
        assert is_job_filtered_out(session, job) is None

    def test_first_matching_rule_wins(self, session, test_users, test_job_scraping_service_log) -> None:
        job = self._make_scraped_job(
            session, test_users[0].id, test_job_scraping_service_log.id, title="Python Developer", company="Acme"
        )
        rule1 = self._make_scraping_filter(
            session, test_users[0].id, type="title", operator="contains", value="python", case_sensitive=False
        )
        self._make_scraping_filter(
            session, test_users[0].id, type="company", operator="equals", value="acme", case_sensitive=False
        )
        result = is_job_filtered_out(session, job)
        assert result is not None
        assert result.id == rule1.id
