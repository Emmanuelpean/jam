"""Selenium test for stale tour data cleanup on page reload.

When a tour is interrupted (e.g. browser refresh) without clicking Done or Skip,
the entities seeded by the tour remain in the database.  On the next app load,
DataContext scans for entities with is_tour=True and deletes them automatically.

The follow-up-email tour seeds:
  - 1 Company  : "NovaTech Solutions"  (Company.is_tour)
  - 2 Persons  : "Johnson" / "Mitchell" (Person.is_tour)
  - 1 Job      : linked to the company (Job.is_tour)
  - 1 Interview: linked to the job     (Interview.is_tour)
"""

import time

from app import models
from base_test import BaseTest

TOUR_ID = "follow-up-email"


class TestStaleTourDataCleanup(BaseTest):
    user_index = 0
    page_url = "jobs"

    def setup_function(self, request) -> None:
        self.login()

    # ------------------------------------------------------------------ helpers

    def _poll_marker_gone(self, model_class, timeout: float = 10.0) -> None:
        """Poll the DB until no is_tour rows remain for the current user."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            self.db.expire_all()
            self.db.rollback()
            count = (
                self.db.query(model_class)
                .filter(
                    model_class.owner_id == self.db_user.id,
                    model_class.is_tour == True,
                )
                .count()
            )
            if count == 0:
                return
            time.sleep(0.5)

        self.db.expire_all()
        self.db.rollback()
        remaining = (
            self.db.query(model_class)
            .filter(
                model_class.owner_id == self.db_user.id,
                model_class.is_tour == True,
            )
            .all()
        )
        assert not remaining, f"{model_class.__name__} is_tour rows still present after {timeout}s: {[r.id for r in remaining]}"

    # ------------------------------------------------------------------ tests

    def test_stale_data_cleaned_on_reload(self) -> None:
        """Start the follow-up-email tour, reload without finishing, verify cleanup."""
        # Start tour — seeds company, persons, job, interview before showing popover
        self.tour_utils.start_tour(TOUR_ID)
        self.wait_for_page("jobs")

        # Confirm seeded is_tour entities exist in the DB before we reload
        self.db.expire_all()
        self.db.rollback()
        uid = self.db_user.id

        seeded_jobs = (
            self.db.query(models.Job)
            .filter(models.Job.owner_id == uid, models.Job.is_tour == True)
            .all()
        )
        assert len(seeded_jobs) == 1, f"Expected 1 seeded Job, got {len(seeded_jobs)}"

        seeded_persons = (
            self.db.query(models.Person)
            .filter(models.Person.owner_id == uid, models.Person.is_tour == True)
            .all()
        )
        assert len(seeded_persons) == 2, f"Expected 2 seeded persons, got {len(seeded_persons)}"

        # Reload the page — simulates a crash / interrupted tour (endTour is never called)
        self.refresh()

        # DataContext fires the cleanup effect after loading data — poll until rows are gone
        self._poll_marker_gone(models.Interview)
        self._poll_marker_gone(models.Job)
        self._poll_marker_gone(models.Company)
        self._poll_marker_gone(models.Person)
