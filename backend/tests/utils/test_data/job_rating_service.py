"""Test data for job rating service related tests."""

JOB_RATING_DATA = [
    {"scraped_job_id": 1, "overall_score": 4, "user_qualification_id": 1, "owner_id": 1},
    {"scraped_job_id": 2, "overall_score": 8, "user_qualification_id": 2, "owner_id": 1},
]

JOB_RATING_SERVICE_LOG_DATA = [
    {
        "run_duration": 0.85,
        "run_datetime": "2025-01-15T12:34:56+00:00",
        "is_success": True,
        "error_message": None,
        "rated_job_found_ids": [101, 102, 103],
        "rated_job_succeeded_ids": [101, 102],
        "rated_job_failed_ids": [103],
        "rated_job_skipped_ids": [],
    },
    {
        "run_duration": 1.23,
        "run_datetime": "2025-02-01T09:00:00+00:00",
        "is_success": False,
        "error_message": "Timeout contacting rating service",
        "rated_job_found_ids": [201, 202],
        "rated_job_succeeded_ids": [201],
        "rated_job_failed_ids": [202],
        "rated_job_skipped_ids": [],
    },
    {
        "run_duration": 3,
        "run_datetime": "2025-03-10T18:00:00+00:00",
        "is_success": None,
        "error_message": None,
        "rated_job_found_ids": [],
        "rated_job_succeeded_ids": [],
        "rated_job_failed_ids": [],
        "rated_job_skipped_ids": [301],
    },
]
