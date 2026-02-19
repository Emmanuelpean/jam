import pytest


@pytest.fixture
def data(scrape):
    driver = scrape("linkedin_job.html")
    return driver.execute_script("return scrapeLinkedInJob();")


def test_title(data):
    assert data["title"] == "Senior Python Engineer"


def test_company(data):
    assert data["company"] == "Acme Ltd"


def test_platform(data):
    assert data["platform"] == "linkedin"


def test_location(data):
    assert data["location"] == "London, England, United Kingdom"


def test_attendance_type(data):
    assert data["attendance_type"] == "hybrid"


def test_salary(data):
    assert data["salary_min"] == 50_000
    assert data["salary_max"] == 70_000
    assert data["salary_currency"] == "GBP"


def test_description_has_bullets(data):
    assert "- 5+ years of Python experience" in data["description"]
    assert "- Docker and Kubernetes" in data["description"]


def test_description_no_blank_lines_between_bullets(data):
    lines = data["description"].splitlines()
    bullet_indices = [i for i, line in enumerate(lines) if line.startswith("- ")]
    for i in range(len(bullet_indices) - 1):
        gap = bullet_indices[i + 1] - bullet_indices[i]
        assert gap == 1, f"Blank line between bullets at line {bullet_indices[i]}"