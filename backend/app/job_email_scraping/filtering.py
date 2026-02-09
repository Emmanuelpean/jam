"""Logic for filtering scraped jobs based on user-defined rules."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.job_email_scraping.models import ScrapedJob, ScrapingExclusionFilter, ScrapingFavouriteFilter

STRING_OPERATORS = [
    "contains",
    "equals",
    "starts_with",
    "ends_with",
    "not_contains",
    "not_equals",
]


def apply_rule_to_values(
    job_value: str | float | int,
    rule_value: str | float | int,
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
    job: ScrapedJob | ScrapingFavouriteFilter,
    job_filter: ScrapingExclusionFilter,
) -> bool:
    """Check if a job matches a given filter rule using Python logic.
    :param job: The ScrapedJob instance to check.
    :param job_filter: The JobFilterRule instance to apply.
    :return: True if the job matches the rule (i.e. should be filtered out)."""

    field_value = getattr(job, job_filter.type, None)
    if field_value is None:
        return False

    return apply_rule_to_values(
        job_value=field_value,
        rule_value=job_filter.value,
        op=job_filter.operator,
        case_sensitive=job_filter.case_sensitive,
    )


def is_job_filtered_out(
    session: Session,
    job: ScrapedJob,
) -> ScrapingExclusionFilter | None:
    """Check if a job should be filtered out for a given user based on their rules.
    :param session: SQLAlchemy session for database access.
    :param job: The ScrapedJob instance to check.
    :return: True if the job should be filtered out for the user."""

    rules = (
        session.query(ScrapingExclusionFilter)
        .filter(ScrapingExclusionFilter.owner_id == job.owner_id)
        .filter(ScrapingExclusionFilter.is_active.is_(True))
        .all()
    )

    for rule in rules:
        if job_matches_rule_python(job, rule):
            return rule
    else:
        return None


def is_job_favoured(
    session: Session,
    job: ScrapedJob,
) -> ScrapingExclusionFilter | None:
    """Check if a job should be favoured out for a given user based on their rules.
    :param session: SQLAlchemy session for database access.
    :param job: The ScrapedJob instance to check.
    :return: True if the job should be filtered out for the user."""

    rules = (
        session.query(ScrapingFavouriteFilter)
        .filter(ScrapingFavouriteFilter.owner_id == job.owner_id)
        .filter(ScrapingFavouriteFilter.is_active.is_(True))
        .all()
    )

    for rule in rules:
        if job_matches_rule_python(job, rule):
            return rule
    else:
        return None


def rule_to_sql_predicate(job_filter: ScrapingExclusionFilter):
    """Convert a rule into a SQLAlchemy expression that matches jobs to EXCLUDE.
    Only applies if the field is not NULL."""

    field = getattr(ScrapedJob, job_filter.type)
    value = job_filter.value
    op = job_filter.operator

    # Case handling for strings (mirror Python logic)
    if not job_filter.case_sensitive and op in STRING_OPERATORS:
        field = func.lower(field)
        value = value.lower()

    # Build the base condition
    if op == "contains":
        condition = field.contains(value)
    elif op == "not_contains":
        condition = ~field.contains(value)
    elif op == "equals":
        condition = field == value
    elif op == "not_equals":
        condition = field != value
    elif op == "starts_with":
        condition = field.startswith(value)
    elif op == "ends_with":
        condition = field.endswith(value)
    # Numeric operators
    else:
        num_value = float(value)
        if op == "less_than":
            condition = field < num_value
        elif op == "greater_than":
            condition = field > num_value
        else:
            raise ValueError(f"Unsupported operator: {op}")

    # CRUCIAL: Only exclude if field is NOT NULL
    return field.isnot(None) & condition
