"""Mocks for platform scrapers"""

from app.job_email_scraping.job_scrapers import JobResult


class MockLinkedinBrightdataJobScraper(object):
    """Mock LinkedIn Scraper that returns fake data"""

    base_url = "https://www.linkedin.com/jobs/view/"
    name = "linkedin"

    # noinspection PyMissingConstructor
    def __init__(
        self,
        job_ids: str | list[str],
        simulate_exception: bool = False,
    ) -> None:
        """Initialise mock scraper without API credentials"""

        # Store job IDs without calling parent constructor to avoid API setup
        self.job_ids = [job_ids] if isinstance(job_ids, str) else job_ids
        self.simulate_exception = simulate_exception

    def scrape_job(self) -> list[JobResult]:
        """Return mock LinkedIn job data"""

        mock_jobs = []

        for i, job_id in enumerate(self.job_ids):
            mock_job = JobResult.model_validate(
                {
                    "company": f"TechCorp {i+1}",
                    "company_id": f"company_{job_id}",
                    "location": "London, UK",
                    "job": {
                        "title": f"Senior Software Engineer {i+1}",
                        "description": f"We are seeking a talented Senior Software Engineer to join our growing team. You will work on cutting-edge technologies and collaborate with cross-functional teams to deliver high-quality software solutions. Job ID: {job_id}",
                        "url": f"https://www.linkedin.com/jobs/view/{job_id}",
                        "raw_url": f"https://www.linkedin.com/jobs/view/{job_id}/dfsdgdgsad",
                        "salary": {"min_amount": 60000.0 + (i * 5000), "max_amount": 80000.0 + (i * 5000)},
                    },
                    "raw": str(
                        {
                            "job_id": job_id,
                            "company_name": f"TechCorp {i+1}",
                            "job_title": f"Senior Software Engineer {i+1}",
                            "job_location": "London, UK",
                            "job_summary": f"We are seeking a talented Senior Software Engineer to join our growing team. You will work on cutting-edge technologies and collaborate with cross-functional teams to deliver high-quality software solutions. Job ID: {job_id}",
                            "url": f"https://www.linkedin.com/jobs/view/{job_id}",
                            "base_salary": {
                                "currency": "GBP",
                                "payment_period": "yr",
                                "min_amount": 60000.0 + (i * 5000),
                                "max_amount": 80000.0 + (i * 5000),
                            },
                        }
                    ),
                }
            )
            mock_jobs.append(mock_job)

        return mock_jobs


class MockIndeedBrightdataJobScraper(object):
    """Mock Indeed Scraper that returns fake data"""

    base_url = "https://www.indeed.com/viewjob?jk="
    name = "indeed"

    # noinspection PyMissingConstructor
    def __init__(
        self,
        job_ids: str | list[str],
        simulate_exception: bool = False,
    ) -> None:
        """Initialise mock scraper without API credentials"""

        # Store job IDs without calling parent constructor to avoid API setup
        self.job_ids = [job_ids] if isinstance(job_ids, str) else job_ids
        self.simulate_exception = simulate_exception

    def scrape_job(self) -> list[JobResult]:
        """Return mock Indeed job data"""

        mock_jobs = []

        for i, job_id in enumerate(self.job_ids):
            mock_job = JobResult.model_validate(
                {
                    "company": f"InnovateLtd {i+1}",
                    "company_id": f"https://www.indeed.com/cmp/innovate-ltd-{i+1}",
                    "location": "Manchester, UK",
                    "job": {
                        "title": f"Full Stack Developer {i+1}",
                        "description": f"Join our dynamic team as a Full Stack Developer! You'll be responsible for developing both frontend and backend applications using modern technologies. Great opportunity for growth and learning. Job ID: {job_id}",
                        "url": f"https://www.indeed.com/viewjob?jk={job_id}",
                        "raw_url": f"https://www.indeed.com/viewjob?jk={job_id}&from=some_source",
                        "salary": {"min_amount": 45000.0 + (i * 3000), "max_amount": 65000.0 + (i * 3000)},
                    },
                    "raw": str(
                        {
                            "job_id": job_id,
                            "company_name": f"InnovateLtd {i+1}",
                            "company_url": f"https://www.indeed.com/cmp/innovate-ltd-{i+1}",
                            "job_title": f"Full Stack Developer {i+1}",
                            "location": "Manchester, UK",
                            "description_text": f"Join our dynamic team as a Full Stack Developer! You'll be responsible for developing both frontend and backend applications using modern technologies. Great opportunity for growth and learning. Job ID: {job_id}",
                            "url": f"https://www.indeed.com/viewjob?jk={job_id}",
                            "salary_formatted": f"£{45000 + (i * 3000):,} - £{65000 + (i * 3000):,} a year",
                        }
                    ),
                }
            )
            mock_jobs.append(mock_job)

        return mock_jobs


class MockVeganJobsBrightdataJobScraper(object):
    """Mock VeganJobs Scraper that returns fake data"""

    base_url = "https://www.veganjobs.com/job/"
    name = "veganjobs"

    def __init__(self, job_id: str, simulate_exception: bool = False) -> None:
        """Initialise mock scraper without API credentials"""

        # Store job IDs without calling parent constructor to avoid API setup
        self.job_id = job_id
        self.simulate_exception = simulate_exception

    def scrape_job(self) -> list[JobResult]:
        """Return mock VeganJobs job data"""

        return [
            JobResult.model_validate(
                {
                    "company": "Sharpen Strategy",
                    "company_id": None,
                    "location": "Remote (USA)",
                    "job": {
                        "job_id": self.job_id,
                        "title": "Operations Coordinator",
                        "description": "The deadline to apply for this position is September 30, 2025.\nSharpen Strategy is hiring an Operations Coordinator to help keep our operations and programs running smoothly.",
                        "url": f"https://veganjobs.com/job/{self.job_id}",
                        "raw_url": f"https://veganjobs.com/job/{self.job_id}?ref=api",
                        "salary": {"min_amount": None, "max_amount": None},
                    },
                    "raw": "raw data",
                }
            )
        ]


class MockNhsBrightdataJobScraper(object):
    """Mock NHS Scraper that returns fake data"""

    base_url = "https://beta.jobs.nhs.uk/candidate/jobadvert/"
    name = "nhs"

    # noinspection PyMissingConstructor
    def __init__(self, job_id: str, simulate_exception: bool = False) -> None:
        """Initialise mock scraper without API credentials"""

        # Store job IDs without calling parent constructor to avoid API setup
        self.job_id = job_id
        self.simulate_exception = simulate_exception

    def scrape_job(self) -> list[JobResult]:
        """Return mock NHS job data"""

        return [
            JobResult.model_validate(
                {
                    "company": "Sharpen Strategy",
                    "company_id": None,
                    "location": "Remote (USA)",
                    "job": {
                        "job_id": self.job_id,
                        "title": "Operations Coordinator",
                        "description": "The deadline to apply for this position is September 30, 2025.\nSharpen Strategy is hiring an Operations Coordinator to help keep our operations and programs running smoothly.",
                        "url": f"https://beta.jobs.nhs.uk/candidate/jobadvert/{self.job_id}",
                        "raw_url": f"https://beta.jobs.nhs.uk/candidate/jobadvert/{self.job_id}?ref=api",
                        "salary": {"min_amount": None, "max_amount": None},
                    },
                    "raw": "raw data",
                }
            )
        ]
