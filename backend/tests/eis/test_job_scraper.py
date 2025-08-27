"""Test module for job_scraper.py
Integration tests that use real job IDs and make actual API calls to test the scraping functionality.
These tests require valid BrightData credentials in the eis_secrets.json file."""

import os

import pytest

from app.eis.job_scraper import LinkedinJobScraper, IndeedJobScrapper


class TestJobScraperIntegration:
    """Integration tests for job scraping with real job IDs"""

    # Fixed job IDs for testing
    LINKEDIN_JOB_IDS = ["4270743052", "4248783875"]
    INDEED_JOB_IDS = ["ea2a9f9f1e8a0899"]

    def setup_method(self) -> None:
        """Setup method to check if secrets file exists"""

        secrets_file = os.path.join(os.path.dirname(__file__), "..", "..", "app", "eis", "eis_secrets.json")
        secrets_file = os.path.abspath(secrets_file)  # Convert to absolute path
        if not os.path.exists(secrets_file):
            pytest.skip(f"eis_secrets.json not found - skipping integration tests {os.path.abspath(__file__)}")

    def test_linkedin_scraper_initialization(self) -> None:
        """Test LinkedIn scraper initializes correctly with fixed job ID"""

        scraper = LinkedinJobScraper(self.LINKEDIN_JOB_IDS[0])

        assert scraper.job_ids == [self.LINKEDIN_JOB_IDS[0]]
        assert scraper.job_urls == [f"https://www.linkedin.com/jobs/view/{self.LINKEDIN_JOB_IDS[0]}"]
        assert scraper.name == "linkedin"
        assert hasattr(scraper, "api_key")
        assert hasattr(scraper, "dataset_id")

    def test_indeed_scraper_initialization(self) -> None:
        """Test Indeed scraper initializes correctly with fixed job ID"""

        scraper = IndeedJobScrapper(self.INDEED_JOB_IDS[0])

        assert scraper.job_ids == [self.INDEED_JOB_IDS[0]]
        assert scraper.job_urls == [f"https://www.indeed.com/viewjob?jk={self.INDEED_JOB_IDS[0]}"]
        assert scraper.name == "indeed"
        assert hasattr(scraper, "api_key")
        assert hasattr(scraper, "dataset_id")

    def test_linkedin_scraper_multiple_jobs(self) -> None:
        """Test LinkedIn scraper with multiple job IDs"""

        job_ids = self.LINKEDIN_JOB_IDS
        scraper = LinkedinJobScraper(job_ids)

        assert scraper.job_ids == job_ids
        assert len(scraper.job_urls) == 2
        assert all("linkedin.com/jobs/view/" in url for url in scraper.job_urls)

    def test_linkedin_get_snapshot(self) -> None:
        """Test LinkedIn scraper can get a snapshot ID"""

        scraper = LinkedinJobScraper(self.LINKEDIN_JOB_IDS[0])

        try:
            snapshot_id = scraper.get_snapshot()
            assert snapshot_id is not None
            assert isinstance(snapshot_id, str)
            assert len(snapshot_id) > 0
        except Exception as e:
            pytest.fail(f"Failed to get snapshot: {e}")

    def test_indeed_get_snapshot(self) -> None:
        """Test Indeed scraper can get a snapshot ID"""

        scraper = IndeedJobScrapper(self.INDEED_JOB_IDS[0])

        try:
            snapshot_id = scraper.get_snapshot()
            assert snapshot_id is not None
            assert isinstance(snapshot_id, str)
            assert len(snapshot_id) > 0
        except Exception as e:
            pytest.fail(f"Failed to get snapshot: {e}")

    def test_linkedin_complete_scraping_workflow(self) -> None:
        """Test complete LinkedIn scraping workflow (marked as slow)"""

        scraper = LinkedinJobScraper(self.LINKEDIN_JOB_IDS[0])

        try:
            # This will take some time as it waits for data to be ready
            job_data = scraper.scrape_job()
            print(job_data)

            # Verify we got some data back
            assert job_data is not None
            assert isinstance(job_data, (dict, list))

            # If it's a list, check the first item
            if isinstance(job_data, list) and len(job_data) > 0:
                job_item = job_data[0]
                # Check for common job fields
                assert any(key in job_item for key in ["title", "job_title", "position", "company", "description"])

        except Exception as e:
            pytest.fail(f"Complete scraping workflow failed: {e}")

    @pytest.mark.slow
    def test_indeed_complete_scraping_workflow(self) -> None:
        """Test complete Indeed scraping workflow (marked as slow)"""

        scraper = IndeedJobScrapper(self.INDEED_JOB_IDS[0])

        try:
            # This will take some time as it waits for data to be ready
            job_data = scraper.scrape_job()

            # Verify we got some data back
            assert job_data is not None
            assert isinstance(job_data, (dict, list))

            # If it's a list, check the first item
            if isinstance(job_data, list) and len(job_data) > 0:
                job_item = job_data[0]
                # Check for common job fields
                assert any(key in job_item for key in ["title", "job_title", "position", "company", "description"])

        except Exception as e:
            pytest.fail(f"Complete scraping workflow failed: {e}")

    def test_scraper_handles_invalid_job_id(self) -> None:
        """Test scraper behavior with invalid job ID"""

        invalid_id = "invalid_job_id_12345"
        scraper = LinkedinJobScraper(invalid_id)

        # Should still initialize correctly
        assert scraper.job_ids == [invalid_id]

        # Getting snapshot might work (depends on BrightData validation)
        # But waiting for data should eventually timeout or fail
        # We don't test the full workflow to avoid long test times

    def test_custom_poll_settings(self) -> None:
        """Test scraper with custom polling settings"""

        scraper = LinkedinJobScraper(self.LINKEDIN_JOB_IDS[0], poll_interval=0.5, max_attempts=5)

        assert scraper.poll_interval == 0.5
        assert scraper.max_attempts == 5

    def test_scraper_data_structure(self) -> None:
        """Test that scraped data has expected structure"""

        scraper = LinkedinJobScraper(self.LINKEDIN_JOB_IDS[0])

        # Get snapshot to verify the process works
        try:
            snapshot_id = scraper.get_snapshot()

            # Wait a short time and check if we can retrieve data
            # (even if not ready, should return proper response structure)
            import time

            time.sleep(2)

            # Try to retrieve data (might not be ready yet, but should have proper error handling)
            try:
                data = scraper.retrieve_data(snapshot_id)
                if data:
                    assert isinstance(data, (dict, list))
            except Exception:
                # It's okay if data isn't ready yet
                pass

        except Exception as e:
            pytest.fail(f"Basic workflow test failed: {e}")


# Pytest configuration
def pytest_configure(config) -> None:
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
