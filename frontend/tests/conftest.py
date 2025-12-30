"""Fixtures and helper functions for integration tests"""

import json
import os
import platform
import queue
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path

import psutil
import requests
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.select import Select

backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
sys.path.insert(0, backend_path)

import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from react_select import ReactSelect

# noinspection PyUnresolvedReferences
from tests.conftest import (
    session,
    models,
    test_users,
    SQLALCHEMY_DATABASE_URL,
    authorised_clients,
    client,
    tokens,
    test_settings,
    DATABASE_NAME,
    test_interviews,
    test_job_application_updates,
    test_jobs,
)
from tests.conftest import *


LOGS_DIR = Path(os.path.join(os.path.dirname(settings.log_directory), "test_logs"))
LOGS_DIR.mkdir(exist_ok=True)


@pytest.fixture(scope="session", autouse=True)
def set_test_mode() -> Generator[None, None, None]:
    """Set TEST_MODE to true for all tests"""

    os.environ["TEST_MODE"] = "true"
    yield
    # Cleanup after all tests
    os.environ.pop("TEST_MODE", None)


def kill_process_on_port(port) -> bool:
    """Kill any process using the specified port"""

    try:
        print(f"Checking for processes on port {port}...")
        for proc in psutil.process_iter(["pid", "name", "connections"]):
            try:
                connections = proc.info["connections"]
                if connections:
                    for conn in connections:
                        if conn.laddr.port == port:
                            print(f"Found process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}")
                            proc.kill()
                            print(f"Killed process {proc.info['pid']}")
                            return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"Error checking port {port}: {e}")
    return False


def kill_process_tree(parent_pid) -> None:
    """Kill a process and all its children"""

    try:
        parent = psutil.Process(parent_pid)
        children = parent.children(recursive=True)

        print(f"Killing process tree for PID {parent_pid}")
        print(f"Found {len(children)} child processes")

        # Kill children first
        for child in children:
            try:
                print(f"Killing child process {child.pid}")
                child.kill()
            except psutil.NoSuchProcess:
                pass

        # Kill parent
        try:
            parent.kill()
            print(f"Killed parent process {parent_pid}")
        except psutil.NoSuchProcess:
            pass

        # Wait for processes to terminate
        gone, alive = psutil.wait_procs(children + [parent], timeout=5)

        if alive:
            print(f"Warning: {len(alive)} processes still alive after kill")
            for proc in alive:
                try:
                    proc.kill()
                except psutil.NoSuchProcess:
                    pass

    except psutil.NoSuchProcess:
        print(f"Process {parent_pid} not found")
    except Exception as e:
        print(f"Error killing process tree {parent_pid}: {e}")


def print_backend_pid() -> None:
    """Print the PID of any backend processes currently running"""

    try:
        backend_processes = []
        for proc in psutil.process_iter(["pid", "name", "cmdline"]):
            try:
                if proc.info["cmdline"] and any("uvicorn" in cmd for cmd in proc.info["cmdline"]):
                    backend_processes.append(f"PID {proc.info['pid']}: {' '.join(proc.info['cmdline'])}")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        if backend_processes:
            print(f"Backend processes found: {backend_processes}")
        else:
            print("No backend processes found - backend may have crashed")

    except Exception as e:
        print(f"Error checking backend processes: {e}")


@pytest.fixture(scope="session")
def test_backend_server() -> Generator[str, None, None]:
    """Start a test backend server for integration tests"""

    print("=" * 60)
    print("STARTING BACKEND SERVER")
    print("=" * 60)

    print_backend_pid()
    kill_process_on_port(8000)

    env = os.environ.copy()
    env["DATABASE_NAME"] = DATABASE_NAME
    env["SQLALCHEMY_DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

    print(f"Using database URL: {SQLALCHEMY_DATABASE_URL}")
    print(f"Backend path: {backend_path}")

    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{backend_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = backend_path

    # CREATE LOG FILES FOR BACKEND OUTPUT
    backend_log_file = LOGS_DIR / "backend_server.log"
    backend_error_file = LOGS_DIR / "backend_errors.log"

    with open(backend_log_file, "w") as log_out, open(backend_error_file, "w") as log_err:
        print(f"Backend logs will be saved to: {backend_log_file}")

        # Start backend with output redirected to files
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=backend_path,
            env=env,
            stdout=log_out,
            stderr=log_err,
            text=True,
        )

        print(f"Backend process started with PID: {process.pid}")

        # Wait for server to start
        api_url = "http://localhost:8000"
        print(f"Waiting for backend server to be ready at {api_url}...")

        for attempt in range(30):
            print(f"Attempt {attempt + 1}/30 - Checking backend server health...")

            if process.poll() is not None:
                # Print last lines from error log
                with open(backend_error_file, "r") as f:
                    error_content = f.read()
                print(f"❌ Backend process died! Return code: {process.poll()}")
                print(f"Last error output:\n{error_content[-1000:]}")  # Last 1000 chars
                raise Exception(f"Backend server process terminated unexpectedly")

            try:
                response = requests.get(f"{api_url}/docs", timeout=3)
                print(f"✅ Backend response status code: {response.status_code}")
                if response.status_code == 200:
                    print("✅ Backend server is ready!")
                    break
            except requests.exceptions.ConnectionError:
                print("Backend connection refused, still starting...")
            except requests.exceptions.Timeout:
                print("Backend request timeout...")
            except Exception as e:
                print(f"Backend unexpected error: {e}")

            time.sleep(1)
        else:
            with open(backend_log_file, "r") as f:
                stdout_content = f.read()
            with open(backend_error_file, "r") as f:
                stderr_content = f.read()

            print("❌ Backend server failed to start after 30 seconds")
            print(f"Backend STDOUT:\n{stdout_content[-1000:]}")
            print(f"Backend STDERR:\n{stderr_content[-1000:]}")
            kill_process_tree(process.pid)
            raise Exception(f"Backend server failed to start")

        print("✅ Backend server startup completed successfully!")
        yield api_url

        # Cleanup
        print("Cleaning up backend server...")
        kill_process_tree(process.pid)
        print("✅ Backend server cleanup completed.")
        print(f"Backend logs saved in: {LOGS_DIR}")
        print_backend_pid()


@pytest.fixture(scope="class")
def test_frontend_server(test_backend_server) -> Generator[str, None, None]:
    """Start a test frontend server for integration tests"""

    print("=" * 60)
    print("STARTING FRONTEND SERVER")
    print("=" * 60)

    # Kill any existing process on port 3000
    kill_process_on_port(3000)
    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Frontend path: {frontend_path}")

    # Set environment variables for frontend
    env = os.environ.copy()
    env["REACT_APP_API_URL"] = test_backend_server  # Use the actual backend URL
    env["PORT"] = "3000"  # Use different port to avoid conflicts
    env["BROWSER"] = "none"  # Don't open browser automatically

    print(f"Environment variables:")
    print(f"  REACT_APP_API_URL: {env['REACT_APP_API_URL']}")
    print(f"  PORT: {env['PORT']}")
    print(f"  BROWSER: {env['BROWSER']}")

    # Find npm executable
    npm_cmd = "npm"
    if os.name == "nt":  # Windows
        npm_path = shutil.which("npm.cmd") or shutil.which("npm")
        if npm_path:
            npm_cmd = npm_path
            print(f"Found npm at: {npm_cmd}")
        else:
            raise Exception("npm not found in PATH")

    # Check prerequisites
    package_json_path = os.path.join(frontend_path, "package.json")
    if not os.path.exists(package_json_path):
        raise Exception(f"package.json not found at: {package_json_path}")

    node_modules_path = os.path.join(frontend_path, "node_modules")
    if not os.path.exists(node_modules_path):
        print("⚠️  node_modules not found, you may need to run 'npm install' first")

    # Start the frontend server
    print("Starting frontend server subprocess...")

    # Use shell=True on Windows for better npm handling
    process = subprocess.Popen(
        f'"{npm_cmd}" start',
        cwd=frontend_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Combine stderr into stdout
        shell=True,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )

    print(f"Frontend process started with PID: {process.pid}")

    # Wait for frontend server to start
    frontend_url = "http://localhost:3000"
    print(f"Waiting for frontend server at {frontend_url}...")
    print("This will take 30-60 seconds for React to compile...")

    def read_output(this_process, this_output_queue) -> None:
        """Read output from the frontend server subprocess and put it in a queue"""
        for _line in iter(this_process.stdout.readline, ""):
            this_output_queue.put(_line.strip())

    output_queue = queue.Queue()
    output_thread = threading.Thread(target=read_output, args=(process, output_queue))
    output_thread.daemon = True
    output_thread.start()

    compiled = False
    for attempt in range(90):  # 90 seconds max
        # Check if process died
        if process.poll() is not None:
            print(f"❌ Frontend process died! Return code: {process.poll()}")
            remaining_output = []
            while not output_queue.empty():
                remaining_output.append(output_queue.get())
            print("Recent output:")
            for line in remaining_output[-10:]:  # Last 10 lines
                print(f"  {line}")
            raise Exception(f"Frontend server process terminated unexpectedly")

        # Print recent output
        recent_lines = []
        while not output_queue.empty():
            line = output_queue.get()
            recent_lines.append(line)

            # Look for compilation success indicators
            if "compiled successfully" in line.lower() or "webpack compiled" in line.lower():
                compiled = True
                print(f"✅ Frontend compiled: {line}")
            elif "failed to compile" in line.lower() or "compilation failed" in line.lower():
                print(f"❌ Frontend compilation failed: {line}")
                raise Exception(f"Frontend compilation failed: {line}")

        # Show recent output every 10 seconds
        if attempt % 10 == 0 and recent_lines:
            print(f"Recent frontend output (attempt {attempt + 1}/90):")
            for line in recent_lines[-3:]:  # Last 3 lines
                print(f"  {line}")

        # Try connecting once compilation is done
        if compiled:
            try:
                response = requests.get(frontend_url, timeout=3)
                if response.status_code == 200:
                    print("✅ Frontend server is ready!")
                    break
                else:
                    print(f"Frontend responded with status: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print("Frontend compiled but connection refused...")
            except requests.exceptions.Timeout:
                print("Frontend request timeout...")
            except Exception as e:
                print(f"Frontend connection error: {e}")

        time.sleep(1)
    else:
        # Frontend failed to start
        print("❌ Frontend server failed to start after 90 seconds")

        # Get remaining output
        remaining_output = []
        while not output_queue.empty():
            remaining_output.append(output_queue.get())

        print("Final frontend output:")
        for line in remaining_output[-20:]:  # Last 20 lines
            print(f"  {line}")

        kill_process_tree(process.pid)
        raise Exception("Frontend server failed to start - see output above")

    print("✅ Frontend server startup completed successfully!")
    yield frontend_url + "/jam"

    # Cleanup - more aggressive process killing
    print("Cleaning up frontend server...")
    print(f"Frontend process PID: {process.pid}")

    # Kill the entire process tree
    kill_process_tree(process.pid)

    # Double-check that port 3000 is free
    time.sleep(2)  # Give processes time to die
    if kill_process_on_port(3000):
        print("Found and killed additional process on port 3000")

    print("✅ Frontend server cleanup completed.")


def contiguous_subdicts(dictionary: dict) -> list[dict]:
    """Return a list of all contiguous sub-dictionaries in the given dictionary.
    :param dictionary: The dictionary to search."""

    keys = list(dictionary.keys())
    n = len(keys)
    results = []
    for size in range(1, n):
        for start in range(n):
            # Generate indices with wrap-around using modulo
            subkeys = [keys[(start + i) % n] for i in range(size)]
            subdict = {k: dictionary[k] for k in subkeys}
            results.append(subdict)
    return [dict()] + results


class BaseUtils(object):
    """Base class for selenium utilities"""

    driver: WebDriver = None
    wait: WebDriverWait = None
    frontend_base_url: str = ""
    db = None

    def go_to_page(self, page) -> None:
        """Helper method to go to a specific page"""

        self.driver.get(f"{self.frontend_base_url}/{page}")
        self.wait_for_page(page)

    def wait_for_page(self, page_url: str) -> None:
        """Wait for the dashboard to load"""

        self.wait.until(ec.url_to_be(f"{self.frontend_base_url}/{page_url}"))

    def get_all_element_ids(self) -> list[str]:
        """Get all element IDs present on the current page"""

        # Find all elements that have an ID attribute
        elements_with_id = self.driver.find_elements(By.XPATH, "//*[@id]")

        # Extract the ID values
        element_ids = []
        for element in elements_with_id:
            element_id = element.get_attribute("id")
            if element_id:
                element_ids.append(element_id)

        return sorted(element_ids)

    def get_element(
        self,
        element_id: str,
        selector: str = By.ID,
        timeout: float = 10.0,
        enabled=True,
    ) -> WebElement:
        """Get an element by its ID.
        :param element_id: ID of the element to get
        :param selector: Selector to use for finding the element
        :param timeout: How long to wait before raising an error
        :param enabled: Whether to wait for the element to be enabled"""

        time.sleep(0.1)
        try:
            wait = WebDriverWait(self.driver, timeout)
            if enabled:
                element = wait.until(ec.element_to_be_clickable((selector, element_id)))
            else:
                element = wait.until(ec.presence_of_element_located((selector, element_id)))
            ActionChains(self.driver).move_to_element(element).perform()
            return element
        except Exception:
            raise AssertionError(f"Could not find element {element_id}\nPossible IDs: {self.get_all_element_ids()}")

    def wait_for_disappear(
        self,
        element_id: str,
        selector: str = By.ID,
        timeout=10.0,
    ) -> None:
        """Wait for an element to disappear from the DOM
        :param element_id: ID of the element to get
        :param selector: Selector to use for finding the element
        :param timeout: How long to wait before raising an error"""

        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(ec.invisibility_of_element_located((selector, element_id)))
        except TimeoutException:
            raise AssertionError(f"Element {element_id} did not disappear")

    @staticmethod
    def set_text(element: WebElement, text: str = "") -> None:
        """Clears the input element"""

        modifier_key = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
        element.send_keys(modifier_key, "a")
        element.send_keys(Keys.DELETE)
        element.send_keys(text)

    def _wait_for_modal_close(self, name: str) -> None:
        """Wait for the modal to close"""

        try:
            self.wait.until(ec.invisibility_of_element_located((By.ID, name)))
        except:
            raise AssertionError(f"{name} is present in: {self.get_all_element_ids()}")

    # ----------------------------------------------------- EMAILS -----------------------------------------------------

    def get_verification_token_from_db(self, email: str) -> str:
        """Helper method to get verification token from database
        :param email: Email of the user to get the token for"""

        user = self.db.query(models.User).filter(models.User.email == email).first()
        token = user.verification_token
        assert token is not None, "Verification token not found in database"
        return token

    @staticmethod
    def get_verification_link_from_email(email: str) -> str:
        """Helper method to get verification link from test email endpoint"""

        response = requests.get(f"{settings.backend_url}/test/verification-link/{email}")
        assert response.status_code == 200, f"Failed to get verification link: {response.text}"
        return response.json()["verification_url"]

    @staticmethod
    def get_reset_link_from_email(email: str) -> str:
        """Helper method to get password reset link from test email endpoint"""

        response = requests.get(f"{settings.backend_url}/test/reset-link/{email}")
        assert response.status_code == 200, f"Failed to get reset link: {response.text}"
        return response.json()["reset_url"]

    @staticmethod
    def clear_test_emails() -> None:
        """Helper method to clear all test emails"""

        response = requests.delete(f"{settings.backend_url}/test/emails")
        assert response.status_code == 200, "Failed to clear test emails"

    # ---------------------------------------------------- ELEMENTS ----------------------------------------------------

    def wait_for_delete_modal(self) -> WebElement:
        """Wait for the delete modal to appear"""

        return self.get_element("delete-alert-modal")

    def assert_toast_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        assert error_message in self.get_element("toast").text, f"Message not found: {error_message}"

    @property
    def delete_confirm_button(self) -> WebElement:
        """Get the delete confirm button on the modal"""

        return self.get_element("delete-alert-modal-confirm-button")

    def wait_for_delete_modal_close(self) -> None:
        """Wait for the delete modal to close"""

        self._wait_for_modal_close("delete-alert-modal")


class BaseUtilsClass(BaseUtils):

    def __init__(self, driver: WebDriver, test_frontend_server, session):
        """Object constructor
        :param driver: Selenium WebDriver instance
        :param test_frontend_server: Base URL of the frontend server"""

        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.frontend_base_url = test_frontend_server
        self.db = session


class DataModalUtils(BaseUtilsClass):
    """Base class for testing data modals"""

    def __init__(self, driver, entry_type: str, test_frontend_server, session):
        """Object constructor
        :param driver: Selenium WebDriver
        :param entry_type: Name of the entry type (e.g. tag, company)
        :param test_frontend_server: Frontend server URL
        :param session: requests.Session object for backend API calls"""

        BaseUtilsClass.__init__(self, driver, test_frontend_server, session)
        self.entry_type = entry_type

    # ------------------------------------------------ HELPER FUNCTIONS ------------------------------------------------

    def wait_for_view_modal_close(self) -> None:
        """Wait for the view modal to close"""

        self._wait_for_modal_close(f"modal-view-{self.entry_type}")

    def wait_for_edit_modal_close(self) -> None:
        """Wait for the view modal to close"""

        self._wait_for_modal_close(f"modal-edit-{self.entry_type}")

    def wait_for_view_modal(self) -> WebElement:
        """Wait for the view modal to appear"""

        return self.get_element(f"modal-view-{self.entry_type}")

    def wait_for_edit_modal(self) -> WebElement:
        """Wait for the edit modal to appear"""

        return self.get_element(f"modal-edit-{self.entry_type}")

    def wait_for_import_modal_modal_close(self) -> None:
        """Wait for the import modal to close"""

        self._wait_for_modal_close(f"modal-import-{self.entry_type}")

    def confirm_button(self, mode: str) -> WebElement:
        """Get the confirm button on the modal"""

        return self.get_element(f"modal-{mode}-{self.entry_type}-confirm-button")

    def cancel_button(self, mode: str) -> WebElement:
        """Get the cancel button on the modal"""

        return self.get_element(f"modal-{mode}-{self.entry_type}-cancel-button")

    def edit_button(self, mode: str, **kwargs) -> WebElement:
        """Get the edit button on the modal"""

        return self.get_element(f"modal-{mode}-{self.entry_type}-edit-button", **kwargs)

    def import_button(self) -> WebElement:
        """Get the import button on the modal"""

        return self.get_element(f"modal-import-{self.entry_type}-import-button")

    def delete_button(self, mode: str) -> WebElement:
        """Get the delete button on the modal"""

        return self.get_element(f"modal-{mode}-{self.entry_type}-delete-button")

    def deactivate_button(self) -> WebElement:
        """Get the deactivate button on the modal"""

        return self.get_element(f"modal-view-{self.entry_type}-deactivate-button")

    def activate_button(self) -> WebElement:
        """Get the activate button on the modal"""

        return self.get_element(f"modal-view-{self.entry_type}-activate-button")

    def _fill_modal(self, **values) -> None:
        """Fill the modal with the given values  (key: key of the input elements, value: value to set)."""

        if any(isinstance(v, dict) for v in values.values()):
            for tab_key in values:
                self.get_element(f"{tab_key}-tab").click()
                self._fill_modal(**values[tab_key])
        else:
            self.wait_for_edit_modal()
            for key, value in values.items():
                if key in (
                    "operator",
                    "country",
                    "company_id",
                    "location_id",
                    "job_id",
                    "aggregator_id",
                    "job_application_id",
                    "type",
                    "source",
                    "attendance_type",
                    "applied_via",
                    "application_status",
                ):
                    select = ReactSelect(self.get_element(key))
                    select.open_menu()
                    select.select_by_visible_text(value)
                elif key in ["date", "application_date"]:
                    self.get_element(key + "_set_current").click()
                else:
                    self.set_text(self.get_element(key), value)

    # -------------------------------------------------- VIEW MODALS --------------------------------------------------

    def check_keyword_view_modal(self, entry: models.Keyword) -> None:
        """Helper method to test the view modal for a keyword entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        expected = f"Tag Details\n{entry.name}\nJobs\n({len(entry.jobs)})\nClose\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_aggregator_view_modal(self, entry: models.Aggregator) -> None:
        """Helper method to test the view modal for an aggregator entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        expected = (
            f"Aggregator Details\n{entry.name}\nWebsite\n{entry.url.replace('https://', '')}\nJobs\n({len(entry.jobs)})"
            f"\nJob Applications\n({len(entry.job_applications)})\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_location_view_modal(self, entry: models.Location) -> None:
        """Helper method to test the view modal for a location entry"""

        modal = self.wait_for_view_modal()
        WebDriverWait(self.driver, 30).until(lambda d: "Finding location on map..." not in modal.text)

        # Verify modal contains the entry information
        expected = (
            f"Location Details\nCity\n{entry.city}\nPostcode\n{entry.postcode}"
            f"\nCountry\n{entry.country}\n"
            f"Location on Map\n+\n−\nLeaflet | © OpenStreetMap\n"
            f"Jobs\n({len(entry.jobs)})\nInterviews\n({len(entry.interviews)})\n"
            f"Close\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_company_view_modal(self, entry: models.Company) -> None:
        """Helper method to test the view modal for a company entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        expected = (
            f"Company Details\n{entry.name}\nWebsite\n{entry.url.replace("https://", "")}"
            f"\nDescription\n{entry.description}\nJobs\n({len(entry.jobs)})\nPersons\n({len(entry.persons)})\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_person_view_modal(self, entry: models.Person) -> None:
        """Helper method to test the view modal for a person entry"""

        modal = self.wait_for_view_modal()
        expected = (
            f"Person Details\n{entry.name}\n"
            f"Company\n{entry.company.name.upper()}\nRole\n{entry.role}\n"
            f"Email\n{entry.email}\nPhone\n{entry.phone}\nLinkedIn Profile\nProfile\nRecruiter\n"
            f"Interviews\n({len(entry.interviews)})\nJobs\n({len(entry.jobs)})\nClose\nEdit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_interview_view_modal(self, entry: models.Interview, standalone: bool = True) -> None:
        """Helper method to test the view modal for an interview entry
        :param entry: Interview entry
        :param standalone: Whether the interview is viewed standalone or as part of a job application"""

        modal = self.wait_for_view_modal()
        display_time = entry.date.astimezone()
        entry_type = {"HR": "HR Interview", "Technical": "Technical Interview"}[entry.type]
        if standalone:
            expected = "Interview Details\n" "Job\n" f"{entry.job.title.upper()} ({entry.job.company.name.upper()})\n"
        else:
            expected = "Interview Details\n"
        expected += "Date & Time\n" f"{display_time.strftime("%d/%m/%Y %H:%M")}\n" "Type\n" f"{entry_type}\n"

        if entry.attendance_type and not entry.location:
            expected += f"Location\n{entry.attendance_type.upper()}\n"
        elif entry.location:
            expected += "Location\n" f"{entry.location.name.upper()} ({entry.attendance_type.upper()})\n"
        else:
            expected += "Location\nNot Provided\n"

        if entry.interviewers:
            expected += (
                "Interviewers\n" f"{', '.join([interviewer.name.upper() for interviewer in entry.interviewers])}\n"
            )
        else:
            expected += "Interviewers\nNot Provided\n"

        if entry.note:
            expected += f"Notes\n{entry.note}\n"
        else:
            expected += "Notes\nNot Provided\n"

        expected += "Close\nEdit"

        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_update_view_modal(self, entry: models.JobApplicationUpdate, standalone: bool = True) -> None:
        """Helper method to test the view modal for a job application update entry"""

        modal = self.wait_for_view_modal()
        display_time = entry.date.astimezone()
        if standalone:
            expected = (
                "Job Application Update Details\n"
                "Job\n"
                f"{entry.job.title.upper()} ({entry.job.company.name.upper()})\n"
                "Date & Time\n"
                f"{display_time.strftime("%d/%m/%Y %H:%M")}\n"
                "Type\n"
                f"{entry.type[0].upper() + entry.type[1:]}\n"
                "Notes\n"
                f"{entry.note}\n"
                "Close\n"
                "Edit"
            )
        else:
            expected = (
                "Job Application Update Details\n"
                "Date & Time\n"
                f"{display_time.strftime("%d/%m/%Y %H:%M")}\n"
                "Type\n"
                f"{entry.type[0].upper() + entry.type[1:]}\n"
                "Notes\n"
                f"{entry.note}\n"
                "Close\n"
                "Edit"
            )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_job_view_modal(self, entry: models.Job) -> None:
        """Helper method to test the view modal for a job application update entry"""

        modal = self.wait_for_view_modal()
        expected = "Job Details\nJob Details\nJob Application"
        if entry.application_status:
            expected += f" {entry.application_status.upper()}"
        expected += f"\n{entry.title}\n"
        if entry.company:
            expected += f"Company\n{entry.company.name.upper()}\n"
        else:
            expected += "Company\nNot Provided\n"
        if entry.attendance_type and not entry.location:
            expected += f"Location\n{entry.attendance_type.upper()}\n"
        elif entry.attendance_type and entry.location:
            expected += f"Location\n{entry.location.name.upper()} ({entry.attendance_type.upper()})\n"
        elif not entry.attendance_type and entry.location:
            expected += f"Location\n{entry.location.name.upper()}\n"
        else:
            expected += "Location\nNot Provided\n"
        if entry.description:
            expected += f"Description\n{entry.description}\n"
        else:
            expected += "Description\nNot Provided\n"
        if entry.note:
            expected += f"Notes\n{entry.note}\n"
        else:
            expected += "Notes\nNot Provided\n"
        salary_range = self.salary_range(entry)
        if salary_range:
            expected += f"Salary Range\n{salary_range}\n"
        else:
            expected += "Salary Range\nNot Provided\n"
        expected += "Personal Rating\n"
        if not entry.personal_rating:
            expected += "Not Provided\n"
        if entry.source:
            expected += f"Source Aggregator\n{entry.source.name.upper()}\n"
        else:
            expected += "Source Aggregator\nNot Provided\n"
        if entry.url:
            expected += f"Job URL\n{entry.url.replace('https://', '')}\n"
        else:
            expected += "Job URL\nNot Provided\n"
        if entry.keywords:
            expected += f"Tags\n{'\n'.join([tag.name.upper() for tag in entry.keywords])}\n"
        else:
            expected += "Tags\nNot Provided\n"
        if entry.contacts:
            expected += f"Contacts\n{'\n'.join([person.name.upper() for person in entry.contacts])}\n"
        else:
            expected += "Contacts\nNot Provided\n"
        if entry.deadline:
            expected += f"Application Deadline\n{entry.deadline.strftime('%d/%m/%Y')}\n"
        else:
            expected += "Application Deadline\nNot Provided\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Job Application
        self.get_element("application-tab").click()
        expected = "Job Details\nJob Details\n"
        if entry.application_status:
            expected += f"Job Application {entry.application_status.upper()}\n"
        else:
            expected += "Job Application\n"
        if entry.application_date:
            display_time = entry.application_date.astimezone()
            expected += f"Application Date\n{display_time.strftime("%d/%m/%Y")}\n"
        else:
            expected += "Date\nNot Provided\n"
        if entry.application_status:
            expected += f"Status\n{entry.application_status.upper()}\n"
        else:
            expected += "Status\nNot Provided\n"
        if entry.applied_via == "aggregator" and entry.application_aggregator:
            expected += f"Applied Via\n{entry.application_aggregator.name.upper()}\n"
        elif entry.applied_via:
            expected += f"Applied Via\n{entry.applied_via.upper()}\n"
        else:
            expected += "Applied Via\nNot Provided\n"
        if entry.application_url:
            expected += f"Application URL\n{entry.application_url.replace("https://", "")}\n"
        else:
            expected += "Application URL\nNot Provided\n"
        if entry.note:
            expected += f"Notes\n{entry.application_note}\n"
        else:
            expected += "Notes\nNot Provided\n"
        expected += (
            "Add Interview\n"
            "Date\n"
            "Type\n"
            "Location\n"
            "Notes\n"
            "No Interviews found\n"
            "Add Update\n"
            "Date\n"
            "Type\n"
            "Notes\n"
            "No Updates found\n"
            "Close\n"
            "Edit"
        )
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_speculative_application_view_modal(self, entry: models.SpeculativeApplication) -> None:
        """Helper method to test the view modal for a speculative application entry"""

        modal = self.wait_for_view_modal()
        expected = "Speculative Application Details\n" "Company\n" f"{entry.company.name.upper()}\n"
        if entry.date:
            display_time = entry.date.astimezone()
            expected += f"Date & Time\n{display_time.strftime("%d/%m/%Y %H:%M")}\n"
        else:
            expected += "Date & Time\nNot Provided\n"
        if entry.contact_email:
            expected += f"Contact Email\n{entry.contact_email}\n"
        else:
            expected += "Contact Email\nNot Provided\n"
        if entry.contacts:
            expected += f"Contacts\n{'\n'.join([person.name.upper() for person in entry.contacts])}\n"
        else:
            expected += "Contacts\nNot Provided\n"
        if entry.note:
            expected += f"Notes\n{entry.note}\n"
        else:
            expected += "Notes\nNot Provided\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    @staticmethod
    def salary_range(item: models.Job) -> str | None:
        """
        Returns a formatted salary range string based on minimum and maximum salary values.

        Parameters
        ----------
        item : dict | None
            A dictionary that may contain 'salary_min' and 'salary_max' keys.

        Returns
        -------
        str | None
            A formatted salary string such as:
            - "£30,000"
            - "£30,000 - £40,000"
            - "From £30,000"
            - "Up to £40,000"
            or None if no salary values are provided.
        """
        if not item:
            return None

        salary_min = item.salary_min
        salary_max = item.salary_max

        if not salary_min and not salary_max:
            return None

        if salary_min == salary_max and salary_min:
            return f"£{salary_min:,.0f}"

        if salary_min and salary_max:
            return f"£{salary_min:,.0f} - £{salary_max:,.0f}"

        if salary_min:
            return f"From £{salary_min:,.0f}"

        if salary_max:
            return f"Up to £{salary_max:,.0f}"

        return None

    def add_entry(self, **data) -> None:
        """Add a new entry"""

        self.wait_for_edit_modal()
        self._fill_modal(**data)
        self.confirm_button("edit").click()
        self.wait_for_edit_modal_close()


class DataTableUtils(BaseUtilsClass):
    """Base class for testing data tables"""

    # Parameters needed
    entry_type: str = ""  # entity type of the table (e.g. keywords)

    def __init__(self, driver, entry_type: str, test_frontend_server, session):
        """Object constructor
        :param driver: Selenium WebDriver
        :param entry_type: Name of the entry type (e.g. keywords, companies)
        :param test_frontend_server: Frontend server URL
        :param session: requests.Session object for backend API calls"""

        BaseUtilsClass.__init__(self, driver, test_frontend_server, session)
        self.entry_type = entry_type

    # ----------------------------------------------------- TABLES -----------------------------------------------------

    @property
    def table_rows(self) -> list[WebElement]:
        """Get all table rows on the page"""

        self.get_element("table-row-clickable", By.CLASS_NAME)
        return self.driver.find_elements(By.CSS_SELECTOR, f"[id^='table-row-{self.entry_type}-']")

    def table_row(self, item_id: int, *args, **kwargs) -> WebElement:
        """Get a specific table row by its ID"""

        return self.get_element(f"table-row-{self.entry_type}-{item_id}", *args, **kwargs)

    def context_menu(self, entity_id: int, choice: str) -> None:
        """Row context menu"""

        actions = ActionChains(self.driver)
        actions.context_click(self.table_row(entity_id)).perform()
        self.get_element(f"context-menu-{choice}").click()

    def check_row_exist(self, column: str, name: str, expected_count: int = 1) -> None:
        """Check that a specific row with a specific name exists in the table
        :param column: Name of the column to check
        :param name: Name of the column
        :param expected_count: Expected number of rows with that name"""

        assert (
            self.get_column_values(column).count(name) == expected_count
        ), f"Expected {expected_count} rows with name '{name}'"

    def get_column_values(self, column_key: str | None = None) -> list[str] | list[dict[str, str]]:
        """Get values from a specific table column via the column key
        (matched using id attributes starting with 'table-header-').
        :param column_key: The key of the column. If None, returns all rows as list of dicts.
        :return: List of values from that column, or list of row dicts if no key provided.
        """
        # Find all elements where id starts with 'table-header-'
        header_elements = self.driver.find_elements(By.XPATH, "//*[@id[starts-with(., 'table-header-')]]")
        header_keys = []
        for header in header_elements:
            th_id = header.get_attribute("id")
            # Ensure only ids with "table-header-" are considered
            if th_id and th_id.startswith("table-header-"):
                header_keys.append(th_id[len("table-header-") :])

        # If no column_key provided, return all rows as list of dicts
        if column_key is None:
            rows_data = []
            for row in self.table_rows:
                row_dict = {}
                cells = row.find_elements(By.TAG_NAME, "td")
                for i, key in enumerate(header_keys):
                    if i < len(cells):
                        row_dict[key] = cells[i].text
                rows_data.append(row_dict)
            return rows_data

        if column_key not in header_keys:
            raise ValueError(f"Column key '{column_key}' not found. Available keys: {header_keys}")

        column_index = header_keys.index(column_key)
        return [row.find_elements(By.TAG_NAME, "td")[column_index].text for row in self.table_rows]

    def wait_for_table_load(self, timeout: int | float = 0.1) -> None:
        """Wait for loading spinner to disappear"""

        try:
            WebDriverWait(self.driver, timeout).until(
                ec.invisibility_of_element_located((By.CSS_SELECTOR, "spinner-border"))
            )
        except TimeoutException:
            pass

    def get_row_id(self, index: int) -> int:
        """Get the entry ID of a table row by its index (0-based)
        :param index: Index of the table row"""

        return int(
            re.search(rf"table-row-{self.entry_type}-(\d+)", self.table_rows[index].get_attribute("id")).group(1)
        )

    # ----------------------------------------------------- BUTTONS ----------------------------------------------------

    @property
    def add_entity_button(self) -> WebElement:
        """Get the Add Entity button"""

        return self.get_element(f"add-{self.entry_type}-button")

    def set_page_item_select(self, value) -> None:
        """Set the number of items to display per page
        :param value: Value to select (e.g. "20", "40")"""

        if len(self.table_rows) >= 20:
            Select(self.get_element("page-items-select")).select_by_value(value)

    def table_row_click(self, row_index: int) -> None:
        """Click on a table row by its index (0-based)"""

        element = self.table_row(row_index)
        self.driver.execute_script("arguments[0].click();", element)


class AuthentificationUtils(BaseUtilsClass):
    """Test class for Authentication functionality including:
    - Login with valid credentials
    - Login with invalid credentials
    - Signup with valid data
    - Signup with invalid data
    - Form validation"""

    # ----------------------------------------------------- INPUTS -----------------------------------------------------

    def go_to_login(self) -> None:
        """Go to the login page"""

        self.driver.get(f"{self.frontend_base_url}/login")

    def go_to_register(self) -> None:
        """Go to the register page"""

        self.driver.get(f"{self.frontend_base_url}/register")

    def go_to_forgot_password(self) -> None:
        """Go to the forgot password page"""

        self.driver.get(f"{self.frontend_base_url}/forgot-password")

    def set_email(self, email: str) -> None:
        """Set the email field to the given value"""

        self.get_element("email").send_keys(email)

    def set_password(self, password: str) -> None:
        """Set the password field to the given value"""

        self.get_element("password").send_keys(password)

    def set_confirm_password(self, password: str) -> None:
        """Set the confirm password field to the given value"""

        self.get_element("confirmPassword").send_keys(password)

    def confirm(self) -> None:
        """Confirm the form submission"""

        self.get_element("confirm-button").click()

    def set_terms(self) -> None:
        """Set the accept terms checkbox to True"""

        self.get_element("terms").click()

    def set_first_name(self, value: str) -> WebElement:
        """Get the first name field"""

        return self.get_element("firstName").send_keys(value)

    def set_last_name(self, value: str) -> WebElement:
        """Get the last name field"""

        return self.get_element("lastName").send_keys(value)

    def register_user(
        self,
        email: str,
        password: str,
        first_name: str = "First Name",
        last_name: str = "Last Name",
    ) -> None:
        """Register a new user"""

        self.go_to_register()
        self.set_email(email)
        self.set_password(password)
        self.set_confirm_password(password)
        self.set_terms()
        self.confirm()
        self.set_first_name(first_name)
        self.set_last_name(last_name)
        self.confirm()

    def login_user(self, email: str, password: str) -> None:
        """Login with given credentials"""

        self.go_to_login()
        self.set_email(email)
        self.set_password(password)
        self.confirm()

    # ----------------------------------------------------- ERRORS -----------------------------------------------------

    def _assert_message(self, key: str, message: str) -> None:
        """Assert that the given message is displayed on the page
        :param key: Key to use for finding the error message element
        :param message: Message to check for"""

        assert message in self.get_element(key + "error-message").text, f"Message not found: {message}"

    def assert_email_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("email-", error_message)

    def assert_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("password-", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("confirmPassword-", error_message)

    def assert_accept_terms_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("terms-", error_message)

    # ------------------------------------------------------ PAGES -----------------------------------------------------

    def wait_for_dashboard(self) -> None:
        """Wait for the dashboard to load"""

        self.wait_for_page("dashboard")

    def wait_for_login(self) -> None:
        """Wait for the login page to load"""

        self.wait_for_page("login")

    def wait_for_register(self) -> None:
        """Wait for the register page to load"""

        self.wait_for_page("register")

    def switch_mode(self) -> None:
        """Switch between login and register modes"""

        self.get_element("switch-mode-button").click()

    def go_to_verification_url(self, token: str) -> None:
        """Navigate to login page with verification token"""

        self.driver.get(f"{self.frontend_base_url}/verify-email/?token={token}")

    def switch_to_forgot_password(self) -> None:
        """Navigate to forgot password page"""

        self.get_element("forgot-password-link").click()


class UserSettingsUtils(BaseUtilsClass):
    """Test class for the User Settings Page"""

    @property
    def current_password(self) -> WebElement:
        """Get the current password field"""
        return self.get_element("current_password")

    @property
    def email(self) -> WebElement:
        """Get the email field"""

        return self.get_element("email")

    @property
    def new_password(self) -> WebElement:
        """Get the new password field"""

        return self.get_element("new_password")

    @property
    def confirm_password(self) -> WebElement:
        """Get the confirmation password field"""

        return self.get_element("confirm_password")

    @property
    def theme_hint(self) -> WebElement:
        """Get the theme hint text"""

        return self.get_element("theme-hint")

    @property
    def chase_threshold(self) -> WebElement:
        """Get the chase threshold input"""

        return self.get_element("chase_threshold")

    @property
    def deadline_threshold(self) -> WebElement:
        """Get the deadline threshold input"""

        return self.get_element("deadline_threshold")

    @property
    def update_limit(self) -> WebElement:
        """Get the update limit input"""

        return self.get_element("update_limit")

    def confirm(self) -> None:
        """Confirm the form submission"""

        self.get_element("confirm-button").click()

    def _assert_message(self, key: str, message: str) -> None:
        """Assert that the given message is displayed on the page
        :param key: Key to use for finding the error message element
        :param message: Message to check for"""

        assert message in self.get_element(key + "error-message").text, f"Message not found: {message}"

    def assert_email_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("email-", error_message)

    def assert_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("current_password-", error_message)

    def assert_new_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("new_password-", error_message)

    def assert_confirm_password_error_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        self._assert_message("confirm_password-", error_message)


class BaseTest(BaseUtils):
    """Base class for selenium tests"""

    backend_url = ""  # backend url
    user = None  # user to use
    client = None  # client for the current user
    base_utils = None  # base utils

    # Parameters needed
    page_url = ""  # url of the page to test (not including the base url)
    user_index = 1  # index of the user to use for the test

    _test_name = ""

    company_modal_utils: DataModalUtils = None
    aggregator_modal_utils: DataModalUtils = None
    keyword_modal_utils: DataModalUtils = None
    location_modal_utils: DataModalUtils = None
    person_modal_utils: DataModalUtils = None
    job_modal_utils: DataModalUtils = None
    interview_modal_utils: DataModalUtils = None
    update_modal_utils: DataModalUtils = None
    speculative_application_modal_utils: DataModalUtils = None
    scraped_job_modal_utils: DataModalUtils = None
    scraping_filter_modal_utils: DataModalUtils = None
    company_table_utils: DataTableUtils = None
    aggregator_table_utils: DataTableUtils = None
    keyword_table_utils: DataTableUtils = None
    location_table_utils: DataTableUtils = None
    person_table_utils: DataTableUtils = None
    job_table_utils: DataTableUtils = None
    update_table_utils: DataTableUtils = None
    interview_table_utils: DataTableUtils = None
    scraped_job_table_utils: DataTableUtils = None
    scraping_filter_table_utils: DataTableUtils = None
    auth_utils: AuthentificationUtils = None
    user_settings_utils: UserSettingsUtils = None

    @pytest.fixture(autouse=True)
    def setup_method(
        self,
        test_frontend_server,
        test_backend_server,
        request,
        test_users,
        authorised_clients,
        session,
    ) -> Generator[None, None, None]:
        """Set up the test environment before each test with test data"""
        self._test_name = request.node.name
        try:
            # Configure Chrome options to disable password prompts
            chrome_options = Options()
            prefs = {
                "profile.password_manager_leak_detection": False,
                "credentials_enable_service": False,
                "password_manager_enabled": False,
                "profile.password_manager_enabled": False,
            }
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1960,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--lang=en-GB")

            # Enable verbose logging
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")
            chrome_options.set_capability("goog:loggingPrefs", {"browser": "ALL", "performance": "ALL"})

            self.driver = webdriver.Chrome(options=chrome_options)
            # self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 10)
            # Set timezone using CDP
            self.driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Europe/London"})

            # Set locale using CDP
            self.driver.execute_cdp_cmd("Emulation.setLocaleOverride", {"locale": "en-GB"})

            # Frontend/Backend
            self.frontend_base_url = test_frontend_server
            self.backend_url = test_backend_server

            # Client/User
            self.client = authorised_clients[self.user_index]
            self.user = test_users[self.user_index]
            self.db = session

            self.company_modal_utils = DataModalUtils(self.driver, "company", self.frontend_base_url, self.db)
            self.aggregator_modal_utils = DataModalUtils(self.driver, "aggregator", self.frontend_base_url, self.db)
            self.keyword_modal_utils = DataModalUtils(self.driver, "keyword", self.frontend_base_url, self.db)
            self.location_modal_utils = DataModalUtils(self.driver, "location", self.frontend_base_url, self.db)
            self.person_modal_utils = DataModalUtils(self.driver, "person", self.frontend_base_url, self.db)
            self.job_modal_utils = DataModalUtils(self.driver, "job", self.frontend_base_url, self.db)
            self.interview_modal_utils = DataModalUtils(self.driver, "interview", self.frontend_base_url, self.db)
            self.update_modal_utils = DataModalUtils(
                self.driver, "jobApplicationUpdate", self.frontend_base_url, self.db
            )
            self.speculative_application_modal_utils = DataModalUtils(
                self.driver, "speculative-application", self.frontend_base_url, self.db
            )
            self.scraped_job_modal_utils = DataModalUtils(self.driver, "scrapedJob", self.frontend_base_url, self.db)
            self.scraping_filter_modal_utils = DataModalUtils(
                self.driver, "scrapingFilter", self.frontend_base_url, self.db
            )

            self.company_table_utils = DataTableUtils(self.driver, "company", self.frontend_base_url, self.db)
            self.aggregator_table_utils = DataTableUtils(self.driver, "aggregator", self.frontend_base_url, self.db)
            self.keyword_table_utils = DataTableUtils(self.driver, "keyword", self.frontend_base_url, self.db)
            self.location_table_utils = DataTableUtils(self.driver, "location", self.frontend_base_url, self.db)
            self.person_table_utils = DataTableUtils(self.driver, "person", self.frontend_base_url, self.db)
            self.job_table_utils = DataTableUtils(self.driver, "job", self.frontend_base_url, self.db)
            self.update_table_utils = DataTableUtils(
                self.driver, "jobApplicationUpdate", self.frontend_base_url, self.db
            )
            self.interview_table_utils = DataTableUtils(self.driver, "interview", self.frontend_base_url, self.db)
            self.scraped_job_table_utils = DataTableUtils(self.driver, "scrapedJob", self.frontend_base_url, self.db)
            self.scraping_filter_table_utils = DataTableUtils(
                self.driver, "scrapingFilter", self.frontend_base_url, self.db
            )

            self.auth_utils = AuthentificationUtils(self.driver, self.frontend_base_url, self.db)

            self.user_settings_utils = UserSettingsUtils(self.driver, self.frontend_base_url, self.db)

            self.setup_function(request)

        except Exception:
            if hasattr(self, "driver"):
                try:
                    self._save_browser_logs(failed=True)
                    self.driver.quit()
                except:
                    pass
            raise
        yield  # This allows the test to run

        # Teardown
        try:
            if hasattr(self, "driver"):
                # Check if test failed
                test_failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False

                # Save logs on failure or in CI (always in CI for debugging)
                if test_failed or os.getenv("CI"):
                    self._save_browser_logs(failed=test_failed)
                    self._save_page_screenshot(failed=test_failed)
                self.driver.quit()
        except Exception as e:
            print(f"Error during teardown: {e}")

    def setup_function(self, request) -> None:
        """Function to run before each test - can be overridden in subclasses"""
        pass

    def _save_browser_logs(self, failed: bool = False) -> None:
        """Save browser console logs to file"""
        try:
            # Get browser logs
            browser_logs = self.driver.get_log("browser")
            performance_logs = self.driver.get_log("performance")

            # Create filename with test name and timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            status_string = "FAILED" if failed else "PASSED"
            safe_test_name = self._test_name.replace("/", "_").replace(":", "_")

            # Save browser console logs
            browser_log_file = LOGS_DIR / f"{safe_test_name}_{status_string}_{timestamp}_browser.log"
            with open(browser_log_file, "w") as f:
                f.write(f"Test: {self._test_name}\n")
                f.write(f"Status: {status_string}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"URL: {self.driver.current_url}\n")
                f.write("=" * 80 + "\n\n")

                for entry in browser_logs:
                    f.write(f"[{entry['level']}] {entry['timestamp']}: {entry['message']}\n")

            # Save performance logs (network requests)
            perf_log_file = LOGS_DIR / f"{safe_test_name}_{status_string}_{timestamp}_network.log"
            with open(perf_log_file, "w") as f:
                f.write(f"Test: {self._test_name}\n")
                f.write(f"Network Performance Logs\n")
                f.write("=" * 80 + "\n\n")

                for entry in performance_logs:
                    try:
                        log_entry = json.loads(entry["message"])
                        # Filter for network events
                        if "Network" in log_entry.get("message", {}).get("method", ""):
                            f.write(json.dumps(log_entry, indent=2) + "\n")
                    except:
                        pass

            print(f"✅ Saved browser logs to {browser_log_file}")

        except Exception as e:
            print(f"⚠️ Could not save browser logs: {e}")

    def _save_page_screenshot(self, failed: bool = False) -> None:
        """Save screenshot of current page"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            status_string = "FAILED" if failed else "PASSED"
            safe_test_name = self._test_name.replace("/", "_").replace(":", "_")

            screenshot_file = LOGS_DIR / f"{safe_test_name}_{status_string}_{timestamp}.png"
            self.driver.save_screenshot(str(screenshot_file))
            print(f"✅ Saved screenshot to {screenshot_file}")

        except Exception as e:
            print(f"⚠️ Could not save screenshot: {e}")

    def login(self) -> None:
        """Helper method to log in to the application"""

        self.driver.get(f"{self.frontend_base_url}/login")
        self.get_element("email").send_keys(self.user.email)
        self.get_element("password").send_keys(self.user.plain_password)
        self.get_element("confirm-button").click()
        try:
            self.get_element("loading-spinner", timeout=2)
            self.wait_for_disappear("loading-spinner", timeout=2)
        except:
            pass
        self.wait_for_page("dashboard")
        self.driver.get(f"{self.frontend_base_url}/{self.page_url}")

    # ---------------------------------------------------- DATABASE ----------------------------------------------------

    @property
    def db_user(self) -> models.User:
        """Get the user from the database"""

        self.db.expire_all()
        return self.db.query(models.User).filter(models.User.id == self.user.id).first()

    def verify_user_in_database(self, email: str) -> list[models.User]:
        """Helper method to verify user exists in database"""

        return self.db.query(models.User).filter(models.User.email == email).all()
