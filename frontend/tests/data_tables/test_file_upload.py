"""Tests for CV and cover letter file upload in the job modal."""

import base64
import os
import shutil
import tempfile

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from app.config import settings
from base_test import BaseTest, models


class TestFileUpload(BaseTest):
    """Tests for the file upload widgets (CV and cover letter) on the job application tab."""

    page_url = "jobs"

    def setup_function(self, request) -> None:
        self.test_job = self._make_job(title="File Upload Test Job")
        self.login()

    # -------------------------------------------------- HELPERS --------------------------------------------------

    def _open_job_edit_application_tab(self, job_id: int) -> None:
        """Open the job edit modal and switch to the Application tab."""
        self.job_table_utils.table_context_menu(job_id, "edit")
        self.job_modal_utils.wait_for_edit_modal()
        self.get_element("application-tab").click()

    def _upload_file(self, field_name: str, content: bytes, filename: str) -> None:
        """Write a temp file and send it to the widget's hidden file input."""
        tmp_dir = tempfile.mkdtemp()
        tmp_path = os.path.join(tmp_dir, filename)
        with open(tmp_path, "wb") as f:
            f.write(content)
        try:
            file_input = self.get_element(f"{field_name}-file-input", enabled=False)
            self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
            file_input.send_keys(tmp_path)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    def _wait_for_has_file(self, field_name: str, timeout: int = 10) -> WebElement:
        """Wait for the drop zone to acquire the 'has-file' class and return it."""
        drop_zone = self.get_element(f"{field_name}-drop-zone", enabled=False)
        WebDriverWait(self.driver, timeout).until(lambda _: "has-file" in drop_zone.get_attribute("class"))
        return drop_zone

    def _expand_section(self, section: WebElement, timeout: int = 5) -> None:
        """Expand an accordion section if it is currently collapsed."""
        btn = section.find_element("css selector", ".accordion-button")
        if "collapsed" in btn.get_attribute("class"):
            btn.click()
            WebDriverWait(self.driver, timeout).until(lambda _: "collapsed" not in btn.get_attribute("class"))

    @property
    def document_section(self) -> WebElement:
        """Get the Documents section of the job modal."""

        return self.get_element("application-documents")

    # -------------------------------------------------- TESTS ---------------------------------------------------

    def test_upload_cv(self) -> None:
        """Uploading a CV creates a File record, tags it as 'cv', and links it to the job."""
        initial_count = self.db.query(models.File).count()

        self._open_job_edit_application_tab(self.test_job.id)
        self._upload_file("cv_id", b"My curriculum vitae content", "my_cv.txt")
        drop_zone = self._wait_for_has_file("cv_id")

        assert "my_cv.txt" in drop_zone.text

        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()

        self.db.expire_all()
        assert self.db.query(models.File).count() == initial_count + 1
        job = self.db.query(models.Job).filter_by(id=self.test_job.id).first()
        assert job.cv_id is not None
        file = self.db.query(models.File).filter_by(id=job.cv_id).first()
        assert file.filename == "my_cv.txt"
        assert file.file_type == "cv"

    def test_upload_cover_letter(self) -> None:
        """Uploading a cover letter creates a File record, tags it as 'cover_letter', and links it to the job."""
        initial_count = self.db.query(models.File).count()

        self._open_job_edit_application_tab(self.test_job.id)
        self._upload_file("cover_letter_id", b"Dear Hiring Manager,\n\nI am writing to...", "cover_letter.txt")
        drop_zone = self._wait_for_has_file("cover_letter_id")

        assert "cover_letter.txt" in drop_zone.text

        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()

        self.db.expire_all()
        assert self.db.query(models.File).count() == initial_count + 1
        job = self.db.query(models.Job).filter_by(id=self.test_job.id).first()
        assert job.cover_letter_id is not None
        file = self.db.query(models.File).filter_by(id=job.cover_letter_id).first()
        assert file.filename == "cover_letter.txt"
        assert file.file_type == "cover_letter"

    def test_view_shows_file_card_after_upload(self) -> None:
        """After saving, the view modal Documents section shows the filename, not 'Not Provided'."""
        self._open_job_edit_application_tab(self.test_job.id)
        self._upload_file("cv_id", b"Great CV content", "great_cv.txt")
        self._wait_for_has_file("cv_id")
        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()

        self.job_table_utils.table_row_click(self.test_job.id)
        self.job_modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()

        self._expand_section(self.document_section)
        assert "GREAT_CV.TXT" in self.document_section.text

    def test_view_shows_not_provided_when_no_files(self) -> None:
        """View modal shows 'Not Provided' for both document fields when no files are attached."""
        self.job_table_utils.table_row_click(self.test_job.id)
        self.job_modal_utils.wait_for_view_modal()
        self.get_element("application-tab").click()

        self._expand_section(self.document_section)
        assert self.document_section.text.count("Not Provided") == 2

    def test_file_deduplication(self) -> None:
        """Uploading identical file content twice reuses the same File DB record."""
        job_a = self._make_job(title="Dedup Job A")
        job_b = self._make_job(title="Dedup Job B")
        self.driver.refresh()

        shared_content = b"Identical CV content for deduplication test"

        self._open_job_edit_application_tab(job_a.id)
        self._upload_file("cv_id", shared_content, "shared_cv.txt")
        self._wait_for_has_file("cv_id")
        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()

        self.db.expire_all()
        file_count_after_first = self.db.query(models.File).count()
        first_file_id = self.db.query(models.Job).filter_by(id=job_a.id).first().cv_id

        self._open_job_edit_application_tab(job_b.id)
        self._upload_file("cv_id", shared_content, "shared_cv.txt")
        self._wait_for_has_file("cv_id")
        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()

        self.db.expire_all()
        assert (
            self.db.query(models.File).count() == file_count_after_first
        ), "A duplicate File record was inserted instead of reusing the existing one"
        job_b_refreshed = self.db.query(models.Job).filter_by(id=job_b.id).first()
        assert job_b_refreshed.cv_id == first_file_id, "Second job should reference the same File record as the first"

    def test_oversized_file_rejected_frontend(self) -> None:
        """Uploading a file exceeding max_file_size_mb shows an error and does not create a DB record."""
        initial_count = self.db.query(models.File).count()
        oversized_content = b"x" * (settings.max_file_size_mb * 1024 * 1024 + 1)

        self._open_job_edit_application_tab(self.test_job.id)
        self._upload_file("cv_id", oversized_content, "huge_cv.pdf")

        error_el = WebDriverWait(self.driver, 5).until(lambda d: d.find_element(By.CSS_SELECTOR, ".text-danger.small"))
        assert f"{settings.max_file_size_mb} MB" in error_el.text

        drop_zone = self.get_element("cv_id-drop-zone", enabled=False)
        assert "has-file" not in drop_zone.get_attribute("class")

        self.db.expire_all()
        assert self.db.query(models.File).count() == initial_count

    def test_oversized_file_rejected_backend(self) -> None:
        """The API returns 413 when the reported file size exceeds max_file_size_mb."""
        response = self.client.post(
            "/files/",
            json={
                "filename": "large_cv.pdf",
                "content": "data:application/pdf;base64,dGVzdA==",
                "type": "application/pdf",
                "size": settings.max_file_size_mb * 1024 * 1024 + 1,
                "file_type": "cv",
            },
        )
        assert response.status_code == 413
        assert f"{settings.max_file_size_mb} MB" in response.json()["detail"]

    def test_remove_file_clears_drop_zone(self) -> None:
        """Clicking the remove button clears the file from the drop zone before saving."""
        self._open_job_edit_application_tab(self.test_job.id)
        self._upload_file("cv_id", b"Temporary CV content", "temp_cv.txt")
        drop_zone = self._wait_for_has_file("cv_id")

        self.get_element("cv_id-remove-btn").click()

        WebDriverWait(self.driver, 5).until(lambda _: "has-file" not in drop_zone.get_attribute("class"))
        assert "temp_cv.txt" not in drop_zone.text

        # Confirming without the file should leave the job with no cv_id
        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()

        self.db.expire_all()
        job = self.db.query(models.Job).filter_by(id=self.test_job.id).first()
        assert job.cv_id is None

    def test_cover_letter_pdf_hides_edit_button(self) -> None:
        """Uploading a PDF as a cover letter hides the pencil edit button."""
        self._open_job_edit_application_tab(self.test_job.id)
        self._upload_file("cover_letter_id", b"%PDF-1.4 fake pdf content", "cover_letter.pdf")
        self._wait_for_has_file("cover_letter_id")

        assert not self.check_element_exists(
            "cover_letter_id-write-btn"
        ), "Edit button must not appear when the uploaded cover letter is not a plain-text file"

    def test_cover_letter_write_then_edit(self) -> None:
        """User writes a cover letter via the text editor, saves the job, then reopens and edits it."""
        initial_count = self.db.query(models.File).count()

        self._open_job_edit_application_tab(self.test_job.id)

        # Pencil button is visible when there is no file
        self.get_element("cover_letter_id-write-btn").click()
        self.get_element("cover-letter-text-modal")

        initial_text = "Dear Hiring Manager, I am applying for this role."
        self.get_element("cover_letter_text").send_keys(initial_text)
        self.get_element("cover-letter-text-modal-save-button").click()
        self.wait_for_disappear("cover-letter-text-modal")
        self._wait_for_has_file("cover_letter_id")

        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()

        self.db.expire_all()
        assert self.db.query(models.File).count() == initial_count + 1

        # Reopen the modal and edit the text
        self._open_job_edit_application_tab(self.test_job.id)
        self.get_element("cover_letter_id-write-btn").click()
        self.get_element("cover-letter-text-modal")

        # Wait for the previously saved content to load from the API
        WebDriverWait(self.driver, 10).until(
            lambda d: initial_text[:20] in (d.find_element(By.ID, "cover_letter_text").get_attribute("value") or "")
        )

        updated_text = "Dear Hiring Manager, Updated cover letter content."
        self.set_text(self.get_element("cover_letter_text"), updated_text)
        self.get_element("cover-letter-text-modal-save-button").click()
        self.wait_for_disappear("cover-letter-text-modal")
        self._wait_for_has_file("cover_letter_id")

        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()

        self.db.expire_all()
        job = self.db.query(models.Job).filter_by(id=self.test_job.id).first()
        file = self.db.query(models.File).filter_by(id=job.cover_letter_id).first()
        assert file is not None
        decoded = base64.b64decode(file.content.split(",")[1]).decode("utf-8")
        assert updated_text in decoded

    def test_upload_text_file_then_edit(self) -> None:
        """User uploads a plain-text cover letter file and then edits its content via the text editor."""
        original_text = "Dear Hiring Manager,\n\nI am applying for this role.\n\nKind regards"

        self._open_job_edit_application_tab(self.test_job.id)
        self._upload_file(
            "cover_letter_id",
            original_text.encode("utf-8"),
            "cover_letter.txt",
        )
        self._wait_for_has_file("cover_letter_id")

        # Edit button is visible for text files
        self.get_element("cover_letter_id-write-btn").click()
        self.get_element("cover-letter-text-modal")

        # Textarea is pre-filled with the uploaded file content
        WebDriverWait(self.driver, 10).until(
            lambda d: "applying" in (d.find_element(By.ID, "cover_letter_text").get_attribute("value") or "")
        )

        updated_text = "Dear Hiring Manager,\n\nUpdated content after upload.\n\nKind regards"
        self.set_text(self.get_element("cover_letter_text"), updated_text)
        self.get_element("cover-letter-text-modal-save-button").click()
        self.wait_for_disappear("cover-letter-text-modal")
        self._wait_for_has_file("cover_letter_id")

        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()

        self.db.expire_all()
        job = self.db.query(models.Job).filter_by(id=self.test_job.id).first()
        file = self.db.query(models.File).filter_by(id=job.cover_letter_id).first()
        assert file is not None
        decoded = base64.b64decode(file.content.split(",")[1]).decode("utf-8")
        assert "Updated content after upload." in decoded
