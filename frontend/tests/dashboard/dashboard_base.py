"""Shared base class for dashboard Selenium tests."""

import datetime as dt
import json

from base_test import BaseTest, models
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Default grid dimensions per widget type (mirrors widgetRegistry.ts defaults)
_LAYOUT_DEFAULTS: dict[str, dict] = {
    "metric": {"w": 3, "h": 4, "minW": 2, "minH": 4},
    "table": {"w": 8, "h": 12, "minW": 4, "minH": 8},
    "timeline": {"w": 4, "h": 12, "minW": 3, "minH": 8},
    "graph": {"w": 6, "h": 8, "minW": 4, "minH": 6},
    "map": {"w": 8, "h": 14, "minW": 4, "minH": 10},
}


class DashboardTestBase(BaseTest):
    """Extends BaseTest with helpers for dashboard data creation and layout setup.
    Subclasses must still set `user_index` and call `self.login()` in `setup_function`."""

    page_url = "dashboard"

    # ------------------------------------------------ DATA CREATION ------------------------------------------------

    def _create_job(self, title: str = "Test Job", **kwargs) -> models.Job:
        """Create and persist a Job owned by the current test user."""
        job = models.Job(owner_id=self.user.id, title=title, **kwargs)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def _create_interview(self, job_id: int, date: dt.datetime, **kwargs) -> models.Interview:
        """Create and persist an Interview for the given job."""
        defaults = {"type": "HR"}
        defaults.update(kwargs)
        interview = models.Interview(owner_id=self.user.id, job_id=job_id, date=date, **defaults)
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview

    def _create_update(self, job_id: int, date: dt.datetime, **kwargs) -> models.JobApplicationUpdate:
        """Create and persist a JobApplicationUpdate for the given job."""
        defaults = {"type": "received"}
        defaults.update(kwargs)
        update = models.JobApplicationUpdate(owner_id=self.user.id, job_id=job_id, date=date, **defaults)
        self.db.add(update)
        self.db.commit()
        self.db.refresh(update)
        return update

    def _create_scraped_job(self, title: str = "Scraped Job", **kwargs) -> models.ScrapedJob:
        """Create and persist a ScrapedJob owned by the current test user.

        A JobEmailScrapingServiceLog is created automatically if service_log_id is not provided.
        external_job_id defaults to a per-instance sequential value so multiple calls within
        one test always produce unique IDs without any manual bookkeeping.
        """
        if not hasattr(self, "_scraped_job_seq"):
            self._scraped_job_seq = 0
        self._scraped_job_seq += 1

        if "service_log_id" not in kwargs:
            log = models.JobEmailScrapingServiceLog(run_datetime=dt.datetime.now(dt.timezone.utc))
            self.db.add(log)
            self.db.flush()
            kwargs["service_log_id"] = log.id

        external_job_id = kwargs.pop("external_job_id", f"ext-{self._scraped_job_seq}")
        platform = kwargs.pop("platform", "Indeed")

        scraped_job = models.ScrapedJob(
            owner_id=self.user.id,
            external_job_id=external_job_id,
            platform=platform,
            title=title,
            **kwargs,
        )
        self.db.add(scraped_job)
        self.db.commit()
        self.db.refresh(scraped_job)
        return scraped_job

    def _create_favourite_filter(self, type: str, operator: str, value: str, **kwargs) -> models.ScrapingFavouriteFilter:
        """Create and persist a ScrapingFavouriteFilter owned by the current test user."""
        fav = models.ScrapingFavouriteFilter(
            owner_id=self.user.id,
            type=type,
            operator=operator,
            value=value,
            **kwargs,
        )
        self.db.add(fav)
        self.db.commit()
        self.db.refresh(fav)
        return fav

    def _create_scraped_job_with_failed_rating(self, title: str = "Failed Rating Job", **kwargs) -> models.ScrapedJob:
        """Create a scraped job that has a failed JobRating (is_success=False)."""
        job = self._create_scraped_job(title=title, **kwargs)
        self._create_job_rating(job, is_success=False, llm_model="XX")
        return job

    def _reload(self) -> None:
        """Reload the dashboard page and wait for data to finish loading."""
        self.driver.refresh()
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-loaded='true']"))
        )

    # ----------------------------------------------- LAYOUT HELPERS -----------------------------------------------

    def _set_dashboard_widgets(self, *configs: dict) -> None:
        """Replace the user's dashboard layout with a V3 layout containing only the given widgets.

        Each element in *configs is a WidgetConfig dict, for example:
            {"type": "metric",   "metric": "active_applications"}
            {"type": "timeline", "feed":   "recent_activity"}
            {"type": "table",    "source": "follow_up"}

        Widgets are placed left-to-right in a 12-column grid; a new row starts when the
        next widget would overflow. Call before ``self.login()`` so the page loads with
        the correct layout, or call ``self._reload()`` afterwards to apply the change."""

        col = 0
        row = 0
        widgets = []
        layout = []

        for i, config in enumerate(configs):
            widget_id = f"w-test-{i}"
            dims = _LAYOUT_DEFAULTS.get(config.get("type", "metric"), _LAYOUT_DEFAULTS["metric"])

            if col + dims["w"] > 12:
                col = 0
                row += dims["h"]

            widgets.append({"id": widget_id, "config": config})
            layout.append({"i": widget_id, "x": col, "y": row, **dims})
            col += dims["w"]

        self.user.preferences.dashboard_layout = json.dumps({"version": 3, "widgets": widgets, "layout": layout})
        self.db.commit()
