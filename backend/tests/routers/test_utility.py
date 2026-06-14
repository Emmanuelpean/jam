"""Unit tests for app.routers.utility helper functions."""

import json

from sqlalchemy.dialects import postgresql

from app import models
from app.routers.utility import parse_column_filters


def _sql(condition) -> str:
    """Compile a SQLAlchemy condition to a literal SQL string (no DB needed)."""
    return str(condition.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}))


class TestParseColumnFiltersEdgeCases:
    """None / empty / unrecognised input."""

    def test_none_input_returns_empty(self):
        conditions, joined = parse_column_filters(None, models.JobEmail)
        assert conditions == []
        assert joined == set()

    def test_empty_object_returns_empty(self):
        conditions, joined = parse_column_filters(json.dumps({}), models.JobEmail)
        assert conditions == []
        assert joined == set()

    def test_unknown_column_is_skipped(self):
        filters = json.dumps({"nonexistent_col": {"type": "text", "value": "test"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert conditions == []

    def test_unknown_prefixed_attr_is_skipped(self):
        filters = json.dumps({"job_rating.nonexistent": {"type": "text", "value": "x"}})
        conditions, joined = parse_column_filters(
            filters, models.ScrapedJob, prefixed_models={"job_rating": models.JobRating}
        )
        assert conditions == []
        assert joined == set()

    def test_unknown_filter_type_produces_no_condition(self):
        filters = json.dumps({"subject": {"type": "unknown_type", "value": "x"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert conditions == []


class TestParseColumnFiltersText:
    """type='text' filter."""

    def test_produces_ilike_condition(self):
        filters = json.dumps({"subject": {"type": "text", "value": "python"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
        sql = _sql(conditions[0])
        assert "ILIKE" in sql.upper()
        assert "%python%" in sql

    def test_empty_value_skipped(self):
        filters = json.dumps({"subject": {"type": "text", "value": ""}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert conditions == []

    def test_whitespace_only_value_skipped(self):
        filters = json.dumps({"subject": {"type": "text", "value": "   "}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert conditions == []

    def test_null_value_skipped(self):
        filters = json.dumps({"subject": {"type": "text", "value": None}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert conditions == []


class TestParseColumnFiltersSelect:
    """type='select' filter."""

    def test_produces_in_condition(self):
        filters = json.dumps({"platform": {"type": "select", "selected": ["linkedin", "indeed"]}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
        sql = _sql(conditions[0])
        assert "IN" in sql.upper()
        assert "linkedin" in sql
        assert "indeed" in sql

    def test_empty_list_skipped(self):
        filters = json.dumps({"platform": {"type": "select", "selected": []}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert conditions == []


class TestParseColumnFiltersNumber:
    """type='number' filter — bounds and nullFilter combinations."""

    def test_min_only(self):
        filters = json.dumps({"job_found_n": {"type": "number", "min": 10, "max": None}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
        assert ">= 10" in _sql(conditions[0])

    def test_max_only(self):
        filters = json.dumps({"job_found_n": {"type": "number", "min": None, "max": 50}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
        assert "<= 50" in _sql(conditions[0])

    def test_range_produces_two_conditions(self):
        filters = json.dumps({"job_found_n": {"type": "number", "min": 10, "max": 50}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 2

    def test_no_bounds_produces_no_condition(self):
        filters = json.dumps({"job_found_n": {"type": "number", "min": None, "max": None}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert conditions == []

    def test_null_filter_null_produces_is_null(self):
        filters = json.dumps({"alert_name": {"type": "number", "min": None, "max": None, "nullFilter": "null"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
        assert "IS NULL" in _sql(conditions[0]).upper()

    def test_null_filter_not_null_produces_is_not_null(self):
        filters = json.dumps({"alert_name": {"type": "number", "min": None, "max": None, "nullFilter": "not_null"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
        assert "IS NOT NULL" in _sql(conditions[0]).upper()

    def test_null_filter_not_null_with_range_produces_three_conditions(self):
        filters = json.dumps({"job_found_n": {"type": "number", "min": 5, "max": 20, "nullFilter": "not_null"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        # IS NOT NULL + >= 5 + <= 20
        assert len(conditions) == 3

    def test_null_filter_all_with_range_skips_null_check(self):
        filters = json.dumps({"job_found_n": {"type": "number", "min": 5, "max": 20, "nullFilter": "all"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        # >= 5 + <= 20, no IS NULL/IS NOT NULL
        assert len(conditions) == 2
        sqls = [_sql(c).upper() for c in conditions]
        assert not any("NULL" in s for s in sqls)


class TestParseColumnFiltersDate:
    """type='date' filter."""

    def test_from_only_produces_one_condition(self):
        filters = json.dumps({"date_received": {"type": "date", "from": "2025-01-01", "to": None}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
        assert "2025-01-01" in _sql(conditions[0])

    def test_to_only_produces_one_condition(self):
        filters = json.dumps({"date_received": {"type": "date", "from": None, "to": "2025-12-31"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
        assert "2025-12-31T23:59:59" in _sql(conditions[0])

    def test_to_appends_end_of_day_time(self):
        filters = json.dumps({"date_received": {"type": "date", "from": None, "to": "2025-06-15"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert "T23:59:59" in _sql(conditions[0])

    def test_range_produces_two_conditions(self):
        filters = json.dumps({"date_received": {"type": "date", "from": "2025-01-01", "to": "2025-12-31"}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 2

    def test_no_bounds_produces_no_condition(self):
        filters = json.dumps({"date_received": {"type": "date", "from": None, "to": None}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert conditions == []


class TestParseColumnFiltersReference:
    """type='reference' filter."""

    def test_produces_in_condition_with_int_values(self):
        filters = json.dumps({"service_log_id": {"type": "reference", "selectedIds": ["1", "2", "3"]}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
        sql = _sql(conditions[0])
        assert "IN" in sql.upper()
        assert "1" in sql and "2" in sql and "3" in sql

    def test_empty_list_skipped(self):
        filters = json.dumps({"service_log_id": {"type": "reference", "selectedIds": []}})
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert conditions == []


class TestParseColumnFiltersPrefixedModels:
    """prefixed_models resolution and models_needing_join."""

    def test_prefixed_column_resolves_and_adds_model_to_join_set(self):
        filters = json.dumps({"job_rating.overall_score": {"type": "number", "min": 5, "max": None}})
        conditions, joined = parse_column_filters(
            filters, models.ScrapedJob, prefixed_models={"job_rating": models.JobRating}
        )
        assert len(conditions) == 1
        assert models.JobRating in joined

    def test_primary_model_column_does_not_trigger_join(self):
        filters = json.dumps({"title": {"type": "text", "value": "python"}})
        conditions, joined = parse_column_filters(
            filters, models.ScrapedJob, prefixed_models={"job_rating": models.JobRating}
        )
        assert len(conditions) == 1
        assert joined == set()

    def test_multiple_prefixed_keys_add_model_to_join_set_once(self):
        filters = json.dumps({
            "job_rating.overall_score": {"type": "number", "min": 5, "max": None},
            "job_rating.technical_score": {"type": "number", "min": 6, "max": None},
        })
        conditions, joined = parse_column_filters(
            filters, models.ScrapedJob, prefixed_models={"job_rating": models.JobRating}
        )
        assert len(conditions) == 2
        assert joined == {models.JobRating}

    def test_omitting_prefixed_models_treats_dotted_key_as_unknown(self):
        filters = json.dumps({"job_rating.overall_score": {"type": "number", "min": 5, "max": None}})
        conditions, joined = parse_column_filters(filters, models.ScrapedJob)
        assert conditions == []
        assert joined == set()


class TestParseColumnFiltersMultiple:
    """Multiple keys in a single call."""

    def test_multiple_filters_each_produce_a_condition(self):
        filters = json.dumps({
            "subject": {"type": "text", "value": "python"},
            "platform": {"type": "select", "selected": ["linkedin"]},
            "job_found_n": {"type": "number", "min": 5, "max": None},
        })
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 3

    def test_mix_of_valid_and_invalid_keys(self):
        filters = json.dumps({
            "subject": {"type": "text", "value": "python"},
            "bad_column": {"type": "text", "value": "ignored"},
        })
        conditions, _ = parse_column_filters(filters, models.JobEmail)
        assert len(conditions) == 1
