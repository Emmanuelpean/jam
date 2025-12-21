"""Logic for filtering scraped jobs based on user-defined rules."""

from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app.job_email_scraping.models import ScrapedJob, JobFilter

STRING_OPERATORS = [
    "contains",
    "equals",
    "starts_with",
    "ends_with",
    "not_contains",
    "not_equals",
]


def apply_rule_to_values(
    job_value: Any,
    rule_value: str,
    op: str,
    case_sensitive: bool,
) -> bool:
    """Return True if `value` triggers the rule (i.e. should be filtered out).
    :param job_value: The value from the job to test.
    :param rule_value: The value from the rule to compare against.
    :param op: The operator to use for comparison.
    :param case_sensitive: Whether the comparison should be case-sensitive.
    :return: True if the rule matches (i.e. job should be filtered out)."""

    # Normalise strings for case-insensitive ops
    if isinstance(job_value, str) and not case_sensitive and op in STRING_OPERATORS:
        job_value = job_value.lower()
        rule_value = rule_value.lower()

    # String operators
    if op == "contains":
        return isinstance(job_value, str) and rule_value in job_value
    if op == "not_contains":
        return isinstance(job_value, str) and rule_value not in job_value
    if op == "equals":
        return job_value == rule_value
    if op == "not_equals":
        return job_value != rule_value
    if op == "starts_with":
        return isinstance(job_value, str) and job_value.startswith(rule_value)
    if op == "ends_with":
        return isinstance(job_value, str) and job_value.endswith(rule_value)

    # Numeric operators
    try:
        num_val = float(job_value)
        num_rule = float(rule_value)
    except (TypeError, ValueError):
        return False

    if op == "less_than":
        return num_val <= num_rule
    if op == "greater_than":
        return num_val >= num_rule

    return False


def job_matches_rule_python(
    job: ScrapedJob,
    rule: JobFilter,
) -> bool:
    """Check if a job matches a given filter rule using Python logic.
    :param job: The ScrapedJob instance to check.
    :param rule: The JobFilterRule instance to apply.
    :return: True if the job matches the rule (i.e. should be filtered out)."""

    field_value = getattr(job, rule.filter_type, None)
    if field_value is None:
        return False

    return apply_rule_to_values(
        job_value=field_value,
        rule_value=rule.filter_value,
        op=rule.filter_operator,
        case_sensitive=rule.case_sensitive,
    )


def is_job_filtered_for_user(
    session: Session,
    job: ScrapedJob,
) -> JobFilter | None:
    """Check if a job should be filtered out for a given user based on their rules.
    :param session: SQLAlchemy session for database access.
    :param job: The ScrapedJob instance to check.
    :return: True if the job should be filtered out for the user."""

    rules = (
        session.query(JobFilter).filter(JobFilter.owner_id == job.owner_id).filter(JobFilter.is_active.is_(True)).all()
    )

    for rule in rules:
        if job_matches_rule_python(job, rule):
            return rule
    else:
        return None


def rule_to_sql_predicate(filter: JobFilter) -> ColumnElement[bool]:
    """Convert a rule into a SQLAlchemy expression that matches jobs to EXCLUDE.
    :param filter: The JobFilterRule instance to convert.
    :return: A SQLAlchemy boolean expression representing the rule."""

    field = getattr(ScrapedJob, filter.filter_type)
    value = filter.filter_value
    op = filter.filter_operator

    # Case handling for strings (mirror Python logic)
    if not filter.case_sensitive and op in STRING_OPERATORS:
        field = func.lower(field)
        value = value.lower()

    if op == "contains":
        return field.contains(value)
    if op == "not_contains":
        return ~field.contains(value)
    if op == "equals":
        return field == value
    if op == "not_equals":
        return field != value
    if op == "starts_with":
        return field.startswith(value)
    if op == "ends_with":
        return field.endswith(value)

    # Numeric operators
    num_value = float(value)
    if op == "less_than":
        return field < num_value
    if op == "greater_than":
        return field > num_value

    raise ValueError(f"Unsupported operator: {op}")
