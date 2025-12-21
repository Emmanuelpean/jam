"""Tests for job email scraping filtering logic."""

import pytest

from app.job_email_scraping.filtering import apply_rule_to_values, rule_to_sql_predicate
from app.job_email_scraping.models import ScrapedJobFilter


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
    def create_filter(session, **kwargs) -> ScrapedJobFilter:
        """Helper to create and persist a ScrapedJobFilter."""

        # noinspection PyArgumentList
        rule = ScrapedJobFilter(owner_id=1, **kwargs)
        session.add(rule)
        session.commit()
        return rule

    def test_contains_case_insensitive(self, test_users, session) -> None:
        # Simulate ScrapedJob.title column with a SQLAlchemy column()

        # noinspection PyArgumentList
        rule = self.create_filter(session, type="title", operator="contains", value="python", case_sensitive=False)
        predicate = rule_to_sql_predicate(rule)

        # Ensure predicate is a SQL expression and uses ILIKE/LOWER semantics via contains
        assert str(predicate) == "lower(scraped_job.title) LIKE '%' || :lower_1 || '%'"

    def test_equals_numeric_salary(self, test_users, session) -> None:
        """Test numeric equality operator compiles correctly."""

        rule = self.create_filter(
            session, type="salary_min", operator="less_than", value="100000", case_sensitive=False
        )
        predicate = rule_to_sql_predicate(rule)
        assert str(predicate) == "scraped_job.salary_min < :salary_min_1"

    @pytest.mark.parametrize(
        "filter_type,op,rule_val",
        [
            ("company", "equals", "lower(scraped_job.company) = :lower_1"),
            ("company", "not_equals", "lower(scraped_job.company) != :lower_1"),
            ("title", "starts_with", "lower(scraped_job.title) LIKE :lower_1 || '%'"),
            ("title", "ends_with", "lower(scraped_job.title) LIKE '%' || :lower_1"),
        ],
    )
    def test_string_ops_compile(self, test_users, filter_type, op, rule_val, session) -> None:
        """Test various string operators compile to expected SQL."""

        rule = self.create_filter(session, type=filter_type, operator=op, value=rule_val, case_sensitive=False)
        predicate = rule_to_sql_predicate(rule)
        assert str(predicate) == rule_val
