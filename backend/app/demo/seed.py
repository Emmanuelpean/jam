"""Demo data seeding and cleanup functions.
Reuses test data defined for user 1 (owner_id=1) with proper ID remapping."""

import copy

from sqlalchemy.orm import Session

from app import models
from tests.utils.create_data.utils import create_db_entries, override_properties
from tests.utils.test_data import data_tables
from tests.utils.test_data import job_rating
from tests.utils.test_data import job_scraping
from tests.utils.test_data.utils import add_mappings

PREV_OWNER = 1  # Reuse test data from user 1


def _filter_owner(data: list[dict], new_owner_id: int) -> list[dict]:
    """Deep copy, filter by PREV_OWNER, and set new owner_id.
    :param data: List of dictionaries to filter and remap
    :param new_owner_id: New owner_id to set for filtered entries
    :return: Filtered list of dictionaries with new owner_id set"""

    return [{**entry, "owner_id": new_owner_id} for entry in copy.deepcopy(data) if entry.get("owner_id") == PREV_OWNER]


def _build_index_map(data: list[dict]) -> dict[int, int]:
    """Build mapping from original 1-based position to filtered 1-based position
    for entries belonging to PREV_OWNER.
    :param data: List of dictionaries to build mapping for (must contain owner_id)
    :return: Mapping from original position to filtered position"""

    index_map = {}
    filtered_pos = 1
    for i, entry in enumerate(data):
        if entry.get("owner_id") == PREV_OWNER:
            index_map[i + 1] = filtered_pos
            filtered_pos += 1
    return index_map


def _remap_with_map(
    data: list[dict],
    key: str,
    index_map: dict[int, int],
    objects: list,
) -> list[dict]:
    """Remap FK values using an index map. Drops entries with unmapped references.
    :param data: List of dictionaries to remap
    :param key: Key to remap
    :param index_map: Mapping from original position to filtered position
    :param objects: List of objects to remap against
    :return: Remapped list of dictionaries, with dropped entries if any references were unmapped"""

    result = []
    for entry in data:
        val = entry.get(key)
        if val is not None:
            if val not in index_map:
                continue
            entry[key] = objects[index_map[val] - 1].id
        result.append(entry)
    return result


def _filter_mappings(
    mappings: list[dict],
    primary_key: str,
    secondary_key: str,
    primary_map: dict[int, int],
    secondary_map: dict[int, int] | None = None,
) -> list[dict]:
    """Filter and remap M2M mapping data to only include user 1's entries.
    :param mappings: List of M2M mapping dictionaries to filter and remap
    :param primary_key: Key to filter by for primary table
    :param secondary_key: Key to filter by for secondary table
    :param primary_map: Mapping from original position to filtered position for primary table
    :param secondary_map: Optional mapping from original position to filtered position for secondary table
    :return: Filtered and remapped list of M2M mapping dictionaries"""

    result = []
    for mapping in mappings:
        if mapping[primary_key] not in primary_map:
            continue
        sec_ids = mapping[secondary_key]
        if secondary_map:
            sec_ids = [secondary_map[sid] for sid in sec_ids if sid in secondary_map]
        if sec_ids:
            result.append(
                {
                    primary_key: primary_map[mapping[primary_key]],
                    secondary_key: sec_ids,
                }
            )
    return result


def seed_demo_data(db: Session, user: models.User) -> None:
    """Create all demo data for a user in the demo schema.
    :param db: Database session (bound to demo schema)
    :param user: The demo user to seed data for"""

    owner_id = user.id

    # Geolocations
    geolocations = db.query(models.Geolocation).all()

    # User Qualifications
    qualification_data = [
        {
            "owner_id": owner_id,
            "experience": "5 years of full-stack web development with Python and JavaScript frameworks. "
            "Led a team of 3 developers at a SaaS startup. Built RESTful APIs and microservices.",
            "skills": "Python, JavaScript, TypeScript, React, FastAPI, PostgreSQL, Docker, AWS, Git, CI/CD",
            "education": "BSc Computer Science, University of Manchester (2019)",
            "qualities": "Strong problem-solver, collaborative team player, detail-oriented, adaptable",
            "interests": "Backend engineering, cloud infrastructure, developer tooling, open-source",
        }
    ]
    qualifications = create_db_entries(db, models.UserQualification, qualification_data)

    # Companies
    companies = create_db_entries(db, models.Company, _filter_owner(data_tables.COMPANY_DATA, owner_id))

    # Persons (remap company_id)
    person_data = override_properties(_filter_owner(data_tables.PERSON_DATA, owner_id), ("company_id", companies))
    persons = create_db_entries(db, models.Person, person_data)

    # Keywords
    keywords = create_db_entries(db, models.Keyword, _filter_owner(data_tables.KEYWORD_DATA, owner_id))

    # Aggregators
    aggregators = create_db_entries(db, models.Aggregator, _filter_owner(data_tables.AGGREGATOR_DATA, owner_id))

    # Files
    files = create_db_entries(db, models.File, _filter_owner(data_tables.FILE_DATA, owner_id))

    # Jobs (remap multiple FKs)
    job_data = override_properties(
        _filter_owner(data_tables.JOB_DATA, owner_id),
        ("company_id", companies),
        ("source_aggregator_id", aggregators),
        ("cv_id", files),
        ("cover_letter_id", files),
        ("application_aggregator_id", aggregators),
        ("recruiter_id", persons),
        ("recruitment_company_id", companies),
    )
    jobs = create_db_entries(db, models.Job, job_data)

    # Job M2M mappings (keywords, contacts)
    job_map = _build_index_map(data_tables.JOB_DATA)
    keyword_map = _build_index_map(data_tables.KEYWORD_DATA)
    person_map = _build_index_map(data_tables.PERSON_DATA)

    add_mappings(
        jobs,
        keywords,
        _filter_mappings(data_tables.JOB_KEYWORD_MAPPINGS, "job_id", "keyword_ids", job_map, keyword_map),
        "job_id",
        "keyword_ids",
        "keywords",
    )
    add_mappings(
        jobs,
        persons,
        _filter_mappings(data_tables.JOB_CONTACT_MAPPINGS, "job_id", "person_ids", job_map, person_map),
        "job_id",
        "person_ids",
        "contacts",
    )
    db.flush()

    # Interviews (remap job_id)
    interview_data = override_properties(
        _filter_owner(data_tables.INTERVIEW_DATA, owner_id),
        ("job_id", jobs),
    )
    interviews = create_db_entries(db, models.Interview, interview_data)

    # Interview ↔ Interviewer mappings
    interview_map = _build_index_map(data_tables.INTERVIEW_DATA)
    add_mappings(
        interviews,
        persons,
        _filter_mappings(
            data_tables.INTERVIEW_INTERVIEWER_MAPPINGS, "interview_id", "person_ids", interview_map, person_map
        ),
        "interview_id",
        "person_ids",
        "interviewers",
    )
    db.flush()

    # Job Application Updates (remap job_id)
    app_update_data = override_properties(
        _filter_owner(data_tables.JOB_APPLICATION_UPDATE_DATA, owner_id), ("job_id", jobs)
    )
    create_db_entries(db, models.JobApplicationUpdate, app_update_data)

    # Speculative Applications (remap company_id)
    spec_app_data = override_properties(
        _filter_owner(data_tables.SPECULATIVE_APPLICATION_DATA, owner_id), ("company_id", companies)
    )
    spec_apps = create_db_entries(db, models.SpeculativeApplication, spec_app_data)

    # Speculative application ↔ Contact mappings
    spec_app_map = _build_index_map(data_tables.SPECULATIVE_APPLICATION_DATA)
    add_mappings(
        spec_apps,
        persons,
        _filter_mappings(
            data_tables.SPECULATIVE_APPLICATION_CONTACTS_MAPPING,
            "speculative_application_id",
            "contact_ids",
            spec_app_map,
            person_map,
        ),
        "speculative_application_id",
        "contact_ids",
        "contacts",
    )
    db.flush()

    # Scraping Service Logs (not owner-scoped)
    scraping_log_data = copy.deepcopy(job_scraping.JOB_SCRAPING_SERVICE_LOG_DATA)
    for log in scraping_log_data:
        log["user_found_ids"] = [owner_id] if log["user_found_ids"] else []
        log["user_processed_ids"] = [owner_id] if log["user_processed_ids"] else []
    scraping_logs = create_db_entries(db, models.JobEmailScrapingServiceLog, scraping_log_data)

    # Scraping Exclusion Filters
    filters = create_db_entries(
        db, models.ScrapingExclusionFilter, _filter_owner(job_scraping.SCRAPING_FILTER_DATA, owner_id)
    )

    # Job Emails (remap service_log_id, make external_email_id unique per demo user)
    email_data = override_properties(
        _filter_owner(job_scraping.JOB_EMAIL_DATA, owner_id), ("service_log_id", scraping_logs)
    )
    for entry in email_data:
        entry["external_email_id"] = f"{entry['external_email_id']}_{owner_id}"
    emails = create_db_entries(db, models.JobEmail, email_data)

    # Scraped Jobs (remap service_log_id, exclusion_filter_id, geolocation_id, make external_job_id unique per demo user)
    scraped_job_data = override_properties(
        _filter_owner(job_scraping.SCRAPED_JOB_DATA, owner_id),
        ("service_log_id", scraping_logs),
        ("exclusion_filter_id", filters),
        ("geolocation_id", geolocations),
    )
    for entry in scraped_job_data:
        entry["external_job_id"] = f"{entry['external_job_id']}_{owner_id}"
    scraped_jobs = create_db_entries(db, models.ScrapedJob, scraped_job_data)

    # Email ↔ ScrapedJob mappings (uses index maps for interleaved data)
    email_map = _build_index_map(job_scraping.JOB_EMAIL_DATA)
    scraped_job_map = _build_index_map(job_scraping.SCRAPED_JOB_DATA)

    for mapping in job_scraping.EMAIL_SCRAPEDJOB_MAPPINGS:
        if mapping["email_id"] not in email_map:
            continue
        email_obj = emails[email_map[mapping["email_id"]] - 1]
        for sj_id in mapping["scraped_job_ids"]:
            if sj_id in scraped_job_map:
                email_obj.jobs.append(scraped_jobs[scraped_job_map[sj_id] - 1])
    db.flush()

    # Rating Service Logs (not owner-scoped)
    rating_log_data = copy.deepcopy(job_rating.JOB_RATING_SERVICE_LOG_DATA)
    for log in rating_log_data:
        log["user_found_ids"] = [owner_id] if log["user_found_ids"] else []
        log["user_processed_ids"] = [owner_id] if log["user_processed_ids"] else []
        log["job_found_ids"] = []
        log["job_succeeded_ids"] = []
        log["job_failed_ids"] = []
        log["job_skipped_ids"] = []
    create_db_entries(db, models.JobRatingServiceLog, rating_log_data)

    # Job Ratings (remap scraped_job_id using interleaved index map, remap user_qualification_id)
    ai_system_prompt = db.query(models.AiSystemPrompt).first()
    ai_job_template = db.query(models.AiJobPromptTemplate).first()

    rating_data = _filter_owner(job_rating.JOB_RATING_DATA, owner_id)
    rating_data = _remap_with_map(rating_data, "scraped_job_id", scraped_job_map, scraped_jobs)

    for entry in rating_data:
        # Remap user_qualification_id (user 1's qualifications are consecutive at start)
        qual_id = entry.get("user_qualification_id")
        if qual_id is not None and qual_id <= len(qualifications):
            entry["user_qualification_id"] = qualifications[qual_id - 1].id
        else:
            entry["user_qualification_id"] = qualifications[0].id if qualifications else None
        # Set prompt IDs from demo schema
        entry["system_prompt_id"] = ai_system_prompt.id if ai_system_prompt else None
        entry["job_prompt_template_id"] = ai_job_template.id if ai_job_template else None

    create_db_entries(db, models.JobRating, rating_data)

    db.commit()


def delete_user(db: Session, user_id: int) -> None:
    """Delete a user and all cascade delete all their owned data.
    :param db: Database session (bound to demo schema)
    :param user_id: The ID of the demo user to delete"""

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
