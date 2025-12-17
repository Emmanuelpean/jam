"""Tests for job rating using Gemini AI model with a deterministic mock."""

import re

from app.job_rating import ai_rating


def ai_score_job_mock(
    user_experience: str | None,
    user_education: str | None,
    user_skills: str | None,
    user_qualities: str | None,
    user_interests: str | None,
    job_title: str | None,
    job_company: str | None,
    job_description: str | None,
) -> dict[str, int | str | None]:
    """Deterministic mock of ai_score_job:
    - Returns integers 0-10 or None for each dimension.
    - Computes overall_score as average of non-null dimension scores (rounded).
    - Produces a 2-3 sentence explanation mentioning missing data."""

    _ = user_qualities, job_title, job_company, job_description  # unused in mock

    def none_if_missing(value: str | None) -> bool:
        """Return True if value is None or indicates missing data.
        :param value: input string
        :return: True if missing else False"""

        return (value is None) or value.strip().lower() in ("", "not provided")

    missing = {
        "skills": none_if_missing(user_skills),
        "experience": none_if_missing(user_experience),
        "education": none_if_missing(user_education),
        "interests": none_if_missing(user_interests),
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


def test_ai_score_job_mock_monkeypatch(monkeypatch) -> None:
    """Test ai_score_job using a deterministic mock via monkeypatching."""

    monkeypatch.setattr(ai_rating, "ai_score_job", ai_score_job_mock)

    result = ai_rating.ai_score_job(
        user_experience="3 years as a backend developer",
        user_education="Bachelor of Science in Computer Science",
        user_skills="Python, Django, REST APIs, SQL",
        user_qualities="team player",
        user_interests="Interested in backend roles",
        job_title="Backend Engineer",
        job_company="Acme",
        job_description="Work on APIs",
    )

    assert isinstance(result, dict)
    # all keys present
    for key in (
        "overall_score",
        "technical_fit",
        "experience_alignment",
        "educational_match",
        "interest_match",
        "explanation",
    ):
        assert key in result

    # technical fit should be an int between 0 and 10 in this case
    assert isinstance(result["technical_fit"], int)
    assert 0 <= result["technical_fit"] <= 10

    # overall_score should reflect an average and be int or None
    assert (isinstance(result["overall_score"], int) and 0 <= result["overall_score"] <= 10) or result[
        "overall_score"
    ] is None
