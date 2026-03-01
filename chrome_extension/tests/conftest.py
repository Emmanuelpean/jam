import pytest
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

EXTENSION_DIR = Path(__file__).parent.parent / "dist"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _read_script(filename: str) -> str:
    return (EXTENSION_DIR / filename).read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def driver():
    options = Options()
    options.add_argument(f"--load-extension={EXTENSION_DIR}")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


@pytest.fixture(scope="class")
def scrape(driver):
    """Navigate to a fixture HTML file and inject all content scripts.

    Usage:
        def test_foo(scrape):
            driver = scrape("linkedin_job.html")
            data = driver.execute_script("return scrapeLinkedInJob();")
    """

    def _scrape(fixture_filename: str):
        fixture_path = FIXTURES_DIR / fixture_filename
        driver.get(fixture_path.as_uri())
        # Mock chrome.runtime so the message-listener guard doesn't error
        driver.execute_script("window.chrome = { runtime: { onMessage: { addListener: function() {} } } };")
        for filename in ["content.js"]:
            driver.execute_script(_read_script(filename))
        return driver

    return _scrape
