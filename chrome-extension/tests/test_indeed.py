import pytest


@pytest.fixture
def data(scrape):
    driver = scrape("indeed_main.html")
    return driver.execute_script("return scrapeIndeedJob();")


def test_title(data):
    assert data["title"] == "Data Scientist"


def test_company(data):
    assert data["company"] == "TechCorp"


def test_platform(data):
    assert data["platform"] == "indeed"


def test_location(data):
    assert data["location"] == "Manchester, England"


def test_attendance_type(data):
    assert data["attendance_type"] == "remote"


def test_salary(data):
    assert data["salary_min"] == 40_000
    assert data["salary_max"] == 55_000
    assert data["salary_currency"] == "GBP"


def test_description_has_bullets(data):
    assert "- Python and SQL proficiency" in data["description"]
    assert "- Flexible working hours" in data["description"]


def test_description_no_blank_lines_between_bullets(data):
    lines = data["description"].splitlines()
    bullet_indices = [i for i, line in enumerate(lines) if line.startswith("- ")]
    for i in range(len(bullet_indices) - 1):
        gap = bullet_indices[i + 1] - bullet_indices[i]
        assert gap == 1, f"Blank line between bullets at line {bullet_indices[i]}"
