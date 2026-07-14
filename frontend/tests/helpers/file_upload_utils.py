"""Utilities for the CV and cover letter file upload widgets on the job modal."""

import base64
import os
import shutil
import tempfile

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from app import models
from helpers.jam_test_utils import JamTestUtils
from helpers.data_modal_utils import DataModalUtils
from helpers.data_table_utils import DataTableUtils


class FileUploadUtils(JamTestUtils):
    """Helpers for uploading, editing and reading CV / cover letter files on the application tab."""

    def __init__(self, **kwargs):
        self._init(**kwargs)
        self.job_modal_utils = DataModalUtils(entry_type="job", **kwargs)
        self.job_table_utils = DataTableUtils(entry_type="job", **kwargs)

    def open_job_edit_application_tab(self, job_id: int) -> None:
        """Open the job edit modal and switch to the Application tab."""

        self.job_table_utils.table_context_menu(job_id, "edit")
        self.job_modal_utils.wait_for_edit_modal()
        self.get_element("application-tab").click()

    def upload_file(self, field_name: str, content: bytes, filename: str) -> None:
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

    def wait_for_has_file(self, field_name: str, timeout: int = 10) -> WebElement:
        """Wait for the drop zone to acquire the 'has-file' class and return it."""

        drop_zone = self.get_element(f"{field_name}-drop-zone", enabled=False)
        WebDriverWait(self.driver, timeout).until(lambda _: "has-file" in drop_zone.get_attribute("class"))
        return drop_zone

    def upload_and_wait(self, field_name: str, content: bytes, filename: str) -> WebElement:
        """Upload a file and wait for its drop zone to show it, returning the drop zone."""

        self.upload_file(field_name, content, filename)
        return self.wait_for_has_file(field_name)

    def save_job_edit(self) -> None:
        """Confirm the job edit modal, wait for it to close, and refresh the session."""

        self.job_modal_utils.confirm_button("edit").click()
        self.job_modal_utils.wait_for_edit_modal_close()
        self.db.expire_all()

    def get_job(self, job_id: int) -> models.Job:
        """Fetch a job fresh from the database."""

        self.db.expire_all()
        return self.db.query(models.Job).filter_by(id=job_id).first()

    def get_file(self, file_id: int) -> models.File:
        """Fetch a File row by id."""

        return self.db.query(models.File).filter_by(id=file_id).first()

    @staticmethod
    def decode_file(file: models.File) -> str:
        """Decode a File's base64 data-URI content to text."""

        return base64.b64decode(file.content.split(",")[1]).decode("utf-8")

    def expand_section(self, section: WebElement, timeout: int = 5) -> None:
        """Expand an accordion section and wait for its body to finish opening.

        Bootstrap drops the button's ``collapsed`` class at the *start* of the open animation, so
        that class alone does not mean the body is visible yet. Wait on the collapse container
        instead: fully open is ``show`` present and ``collapsing`` gone."""

        btn = section.find_element("css selector", ".accordion-button")
        collapse = section.find_element("css selector", ".accordion-collapse")
        if "collapsed" in (btn.get_attribute("class") or ""):
            btn.click()
        WebDriverWait(self.driver, timeout).until(
            lambda _: "show" in (collapse.get_attribute("class") or "")
            and "collapsing" not in (collapse.get_attribute("class") or "")
        )

    @property
    def document_section(self) -> WebElement:
        """Get the Documents section of the job modal."""

        return self.get_element("application-documents")
