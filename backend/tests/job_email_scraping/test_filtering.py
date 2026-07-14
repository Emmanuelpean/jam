"""Tests for job email scraping filtering logic."""

import pytest
from sqlalchemy.orm import Session

from app.job_email_scraping.filtering import (
    apply_rule_to_values,
    is_job_filtered_out,
    job_matches_rule_python,
    rule_to_sql_predicate,
)
from app.models import ScrapedJob, ScrapingExclusionFilter
from tests.fixtures.users import FixtureUser


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
            ("90000", "not-a-number", "greater_than", False, False),
            # unknown operator falls through to False
            ("anything", "anything", "unknown_op", False, False),
        ],
    )
    def test_apply_rule_to_values(
        self,
        value: str | float | int,
        rule_val: str,
        op: str,
        case_sensitive: bool,
        expected: bool,
    ) -> None:
        """Test various combinations of values, rule values, operators, and case sensitivity."""

        result = apply_rule_to_values(job_value=value, rule_value=rule_val, op=op, case_sensitive=case_sensitive)
        assert result is expected


class TestRuleToSqlPredicate:

    def test_contains_case_insensitive(self) -> None:
        """Case-insensitive contains compiles to a lowered LIKE predicate."""

        rule = ScrapingExclusionFilter(type="title", operator="contains", value="python", case_sensitive=False)
        predicate = rule_to_sql_predicate(rule)

        expected = "lower(scraped_job.title) IS NOT NULL AND (lower(scraped_job.title) LIKE '%' || :lower_1 || '%')"
        assert str(predicate) == expected

    def test_equals_numeric_salary(self) -> None:
        """Test numeric equality operator compiles correctly."""

        rule = ScrapingExclusionFilter(type="salary_min", operator="less_than", value="100000", case_sensitive=False)
        predicate = rule_to_sql_predicate(rule)
        assert str(predicate) == "scraped_job.salary_min IS NOT NULL AND scraped_job.salary_min < :salary_min_1"

    @pytest.mark.parametrize(
        "type_,operator,value,case_sensitive,expected",
        [
            (
                "title",
                "not_contains",
                "python",
                False,
                "lower(scraped_job.title) IS NOT NULL AND "
                "(lower(scraped_job.title) NOT LIKE '%' || :lower_1 || '%')",
            ),
            (
                "title",
                "equals",
                "python",
                False,
                "lower(scraped_job.title) IS NOT NULL AND lower(scraped_job.title) = :lower_1",
            ),
            (
                "title",
                "not_equals",
                "python",
                False,
                "lower(scraped_job.title) IS NOT NULL AND lower(scraped_job.title) != :lower_1",
            ),
            (
                "title",
                "starts_with",
                "python",
                False,
                "lower(scraped_job.title) IS NOT NULL AND (lower(scraped_job.title) LIKE :lower_1 || '%')",
            ),
            (
                "title",
                "ends_with",
                "python",
                False,
                "lower(scraped_job.title) IS NOT NULL AND (lower(scraped_job.title) LIKE '%' || :lower_1)",
            ),
            (
                "title",
                "contains",
                "Python",
                True,
                "scraped_job.title IS NOT NULL AND (scraped_job.title LIKE '%' || :title_1 || '%')",
            ),
            (
                "salary_min",
                "greater_than",
                "90000",
                False,
                "scraped_job.salary_min IS NOT NULL AND scraped_job.salary_min > :salary_min_1",
            ),
        ],
    )
    def test_operator_predicates(
        self,
        type_: str,
        operator: str,
        value: str,
        case_sensitive: bool,
        expected: str,
    ) -> None:
        """Each supported operator compiles to the expected SQL predicate."""

        rule = ScrapingExclusionFilter(type=type_, operator=operator, value=value, case_sensitive=case_sensitive)
        assert str(rule_to_sql_predicate(rule)) == expected

    def test_unsupported_operator_raises(self) -> None:
        """A numeric-path operator that isn't recognised raises ValueError."""

        rule = ScrapingExclusionFilter(type="salary_min", operator="between", value="5", case_sensitive=False)
        with pytest.raises(ValueError, match="Unsupported operator: between"):
            rule_to_sql_predicate(rule)


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
    def test_string_operators(self, title: str, value: str, op: str, case_sensitive: bool, expected: bool) -> None:
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
    def test_numeric_operators(self, salary: int, value: str, op: str, expected: bool) -> None:
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

    def test_matching_rule_returns_filter(self, session: Session, test_regular_user: FixtureUser) -> None:
        job = test_regular_user.create_scraped_job(title="Python Developer")
        rule = test_regular_user.create_scraping_exclusion_filter(
            type="title", operator="contains", value="python", case_sensitive=False
        )
        result = is_job_filtered_out(session, job)
        assert result is not None
        assert result.id == rule.id

    def test_no_matching_rule_returns_none(self, session: Session, test_regular_user: FixtureUser) -> None:
        job = test_regular_user.create_scraped_job(title="Java Developer")
        test_regular_user.create_scraping_exclusion_filter(
            type="title", operator="contains", value="python", case_sensitive=False
        )
        assert is_job_filtered_out(session, job) is None

    def test_inactive_rule_is_ignored(self, session: Session, test_regular_user: FixtureUser) -> None:
        job = test_regular_user.create_scraped_job(title="Python Developer")
        test_regular_user.create_scraping_exclusion_filter(
            type="title", operator="contains", value="python", case_sensitive=False, is_active=False
        )
        assert is_job_filtered_out(session, job) is None

    def test_rule_from_other_owner_is_ignored(
        self, session: Session, test_regular_user: FixtureUser, test_admin_user: FixtureUser
    ) -> None:
        job = test_regular_user.create_scraped_job(title="Python Developer")
        test_admin_user.create_scraping_exclusion_filter(
            type="title", operator="contains", value="python", case_sensitive=False
        )
        assert is_job_filtered_out(session, job) is None

    def test_first_matching_rule_wins(self, session: Session, test_regular_user: FixtureUser) -> None:
        job = test_regular_user.create_scraped_job(title="Python Developer", company="Acme")
        rule1 = test_regular_user.create_scraping_exclusion_filter(
            type="title", operator="contains", value="python", case_sensitive=False
        )
        test_regular_user.create_scraping_exclusion_filter(
            type="company", operator="equals", value="acme", case_sensitive=False
        )
        result = is_job_filtered_out(session, job)
        assert result is not None
        assert result.id == rule1.id
