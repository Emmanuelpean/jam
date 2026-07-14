"""Pytest fixtures for Job Rating tests"""

import re

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy.orm import Session

import app.job_rating.scraped_job_rating as rating
from app import models
from tests.utils.create_data.utils import create_db_entries


def claude_query_mock(system_prompt: str, llm_prompt: str, max_tokens: int = 1024) -> dict[str, int | str | None]:
    """Deterministic mock of claude_query for testing.
    Parses the system_prompt and llm_prompt to extract candidate/job info and returns
    heuristic-based scores matching the expected output schema.
    :param system_prompt: System prompt containing candidate profile
    :param llm_prompt: The formatted job prompt containing job details
    :param max_tokens: Maximum tokens (unused in mock)
    :return: Dict with scores and explanation matching the AI output schema"""
    _ = max_tokens

    # Candidate info is now in the system prompt; merge both for field extraction
    combined = system_prompt + "\n" + llm_prompt

    def extract_field(prompt: str, field_name: str) -> str | None:
        """Extract a field value from the prompt."""
        pattern = rf"\*\*{field_name}\*\*:\s*(.+?)(?:\n|$)"
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            return None if value.lower() == "not provided" else value
        return None

    # Extract fields from the combined prompt (candidate in system, job in user)
    user_skills = extract_field(combined, "Skills")
    user_experience = extract_field(combined, "Experience")
    user_education = extract_field(combined, "Education")
    user_interests = extract_field(combined, "Interests")

    missing = {
        "skills": user_skills is None,
        "experience": user_experience is None,
        "education": user_education is None,
        "interests": user_interests is None,
    }

    # Technical fit heuristic
    technical_fit = None
    if not missing["skills"]:
        s = user_skills.lower()
        keywords = ["python", "django", "react", "sql", "aws", "docker", "kubernetes", "javascript", "typescript"]
        matches = sum(1 for kw in keywords if kw in s)
        technical_fit = max(0, min(10, int(4 + matches * 1)))  # base 4, +1 per keyword

    # Experience alignment heuristic (try to extract years)
    experience_alignment = None
    if not missing["experience"]:
        exp = user_experience.lower()
        m = re.search(r"(\d+)\s+year", exp)
        if m:
            years = int(m.group(1))
            experience_alignment = max(0, min(10, int(min(10, years * 2))))  # 1 year -> 2, 5 -> 10
        elif "senior" in exp:
            experience_alignment = 9
        elif "junior" in exp:
            experience_alignment = 4
        else:
            experience_alignment = 6

    # Educational match heuristic
    educational_match = None
    if not missing["education"]:
        edu = user_education.lower()
        if "phd" in edu:
            educational_match = 9
        elif "master" in edu:
            educational_match = 8
        elif "bachelor" in edu or "ba" in edu or "bs" in edu:
            educational_match = 7
        else:
            educational_match = 5

    # Interest match heuristic
    interest_match = None
    if not missing["interests"]:
        intr = user_interests.lower()
        if "not interested" in intr or ("not" in intr and "interested" in intr):
            interest_match = 0
        else:
            interest_match = 7

    # Compute overall_score as average of non-null scores
    scores = [v for v in (technical_fit, experience_alignment, educational_match, interest_match) if v is not None]
    overall_score = None
    if scores:
        overall_score = int(round(sum(scores) / len(scores)))

    # Build explanation mentioning missing data
    missing_dims = [k for k, v in missing.items() if v]
    if missing_dims:
        missing_note = " Missing: " + ", ".join(missing_dims) + "."
    else:
        missing_note = ""

    explanation = (
        "This is a deterministic mock assessment based on simple heuristics."
        + missing_note
        + " The scores reflect keyword and years heuristics and are suitable for unit tests."
    )

    return {
        "overall_score": overall_score,
        "technical_fit": technical_fit,
        "experience_alignment": experience_alignment,
        "educational_match": educational_match,
        "interest_match": interest_match,
        "explanation": explanation,
    }


@pytest.fixture(autouse=True)
def mock_ai_score(monkeypatch: MonkeyPatch) -> None:
    """Mock claude_query for all tests"""

    monkeypatch.setattr(rating, "claude_query", claude_query_mock)


@pytest.fixture
def test_rating_service_log(session: Session) -> models.JobRatingServiceLog:
    """Create a job-rating service log."""
    return create_db_entries(session, models.JobRatingServiceLog)[0]
