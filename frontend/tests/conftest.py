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
from contextlib import contextmanager
from typing import Generator, Any

import psutil
import pytest
import requests
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.select import Select

from app import models
from app.config import settings
from app.core.oauth2 import create_access_token

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


pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.clients",
    "tests.fixtures.users",
    "tests.fixtures.test_data",
    "tests.fixtures.job_scraping",
    "tests.fixtures.job_rating",
]


def kill_process_on_port(port) -> bool:
    """Kill any process using the specified port"""
    try:
        print(f"Checking for processes on port {port}...")
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                # Get connections separately, not from info dict
                connections = proc.net_connections()
                if connections:
                    for conn in connections:
                        if hasattr(conn, "laddr") and conn.laddr.port == port:
                            print(f"Found process {proc.info['name']} (PID: {proc.info['pid']}) on port {port}")
                            proc.kill()
                            proc.wait(timeout=5)  # Wait for process to die
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
def frontend_url(worker_id) -> str:
    """Calculate frontend URL for this worker without starting the server"""
    if worker_id == "master":
        port = 3000
    else:
        worker_num = int(worker_id.replace("gw", ""))
        port = 3000 + worker_num + 1  # gw0 -> 3001, gw1 -> 3002, etc.
    return f"http://localhost:{port}"


@pytest.fixture(scope="session")
def test_backend_server(database_url, worker_id, engine, frontend_url) -> Generator[str, None, None]:
    """Start a test backend server for integration tests"""
    print("=" * 60)
    print(f"STARTING BACKEND SERVER (Worker: {worker_id})")
    print("=" * 60)
    print_backend_pid()

    # Determine port based on worker_id
    if worker_id == "master":
        port = 8000
    else:
        # Extract worker number from worker_id (e.g., "gw0" -> 0)
        worker_num = int(worker_id.replace("gw", ""))
        port = 8000 + worker_num + 1  # gw0 -> 8001, gw1 -> 8002, etc.

    print(f"Using port: {port}")
    kill_process_on_port(port)

    env = os.environ.copy()
    env["SQLALCHEMY_DATABASE_URL"] = database_url
    env["TEST_MODE"] = "true"
    env["LOG_DIRECTORY"] = settings.log_directory
    env["FRONTEND_URL"] = frontend_url + "/jam"
    print(f"Using database URL: {database_url}")
    print(f"Backend path: {backend_path}")

    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{backend_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = backend_path

    # CREATE LOG FILES FOR BACKEND OUTPUT
    backend_log_file = settings.log_directory + f"/backend_server_{worker_id}.log"
    backend_error_file = settings.log_directory + f"/backend_errors_{worker_id}.log"

    with open(backend_log_file, "w") as log_out, open(backend_error_file, "w") as log_err:
        print(f"Backend logs will be saved to: {backend_log_file}")

        # Start backend with worker-specific port
        process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(port)],
            cwd=backend_path,
            env=env,
            stdout=log_out,
            stderr=log_err,
            text=True,
        )

        print(f"Backend process started with PID: {process.pid} on port {port}")

        # Wait for server to start
        api_url = f"http://localhost:{port}"
        print(f"Waiting for backend server to be ready at {api_url}...")

        for attempt in range(30):
            print(f"Attempt {attempt + 1}/30 - Checking backend server health...")
            if process.poll() is not None:
                with open(backend_error_file, "r") as f:
                    error_content = f.read()
                print(f"❌ Backend process died! Return code: {process.poll()}")
                print(f"Last error output:\n{error_content[-1000:]}")
                raise Exception(f"Backend server process terminated unexpectedly")

            try:
                response = requests.get(f"{api_url}/health", timeout=3)
                print(f"✅ Backend response status code: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Backend server is ready on port {port}!")
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

        print(f"✅ Backend server startup completed successfully on port {port}!")
        yield api_url

        # Cleanup
        print(f"Cleaning up backend server on port {port}...")
        kill_process_tree(process.pid)
        print("✅ Backend server cleanup completed.")
        print(f"Backend logs saved in: {settings.log_directory}")
        print_backend_pid()


@pytest.fixture(scope="session")
def test_frontend_server(test_backend_server, worker_id, frontend_url) -> Generator[str, None, None]:
    """Start a test frontend server for integration tests"""
    print("=" * 60)
    print(f"STARTING FRONTEND SERVER (Worker: {worker_id})")
    print("=" * 60)

    # Extract port from frontend_url
    port = int(frontend_url.split(":")[-1])
    print(f"Using port: {port}")
    kill_process_on_port(port)

    frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Frontend path: {frontend_path}")

    # Set environment variables for frontend
    env = os.environ.copy()
    env["REACT_APP_API_BASE_URL"] = test_backend_server  # Use worker-specific backend
    env["REACT_APP_API_SERVICE_URL"] = test_backend_server  # Scheduler routes also served by test backend
    env["PORT"] = str(port)
    env["BROWSER"] = "none"
    print(f"Environment variables:")
    print(f"  REACT_APP_API_BASE_URL: {env['REACT_APP_API_BASE_URL']}")
    print(f"  REACT_APP_API_SERVICE_URL: {env['REACT_APP_API_SERVICE_URL']}")
    print(f"  PORT: {env['PORT']}")

    # Find npm executable
    # noinspection PyDeprecation
    npm_cmd = shutil.which("npm") or shutil.which("npm.cmd")
    if not npm_cmd:
        raise Exception("npm not found in PATH")

    print(f"Found npm at: {npm_cmd}")

    # Check prerequisites
    package_json_path = os.path.join(frontend_path, "package.json")
    if not os.path.exists(package_json_path):
        raise Exception(f"package.json not found at: {package_json_path}")

    node_modules_path = os.path.join(frontend_path, "node_modules")
    if not os.path.exists(node_modules_path):
        print("⚠️  node_modules not found, you may need to run 'npm install' first")

    # CREATE LOG FILES FOR FRONTEND OUTPUT
    frontend_log_file = settings.log_directory + f"/frontend_server_{worker_id}.log"
    print(f"Frontend logs will be saved to: {frontend_log_file}")

    # Start the frontend server
    print("Starting frontend server subprocess...")
    process = subprocess.Popen(
        f'"{npm_cmd}" start',
        cwd=frontend_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        text=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )

    print(f"Frontend process started with PID: {process.pid}")

    # Wait for frontend server to start
    frontend_url = f"http://localhost:{port}"
    print(f"Waiting for frontend server at {frontend_url}...")
    print("This will take 30-60 seconds for React to compile...")

    def read_output(this_process, this_output_queue, log_file) -> None:
        """Read output from the frontend server subprocess and put it in a queue"""
        with open(log_file, "w") as log:
            for _line in iter(this_process.stdout.readline, ""):
                line_stripped = _line.strip()
                this_output_queue.put(line_stripped)
                log.write(_line)
                log.flush()

    output_queue = queue.Queue()
    output_thread = threading.Thread(target=read_output, args=(process, output_queue, frontend_log_file))
    output_thread.daemon = True
    output_thread.start()

    compiled = False
    for attempt in range(90):
        if process.poll() is not None:
            print(f"❌ Frontend process died! Return code: {process.poll()}")
            remaining_output = []
            while not output_queue.empty():
                remaining_output.append(output_queue.get())
            print("Recent output:")
            for line in remaining_output[-10:]:
                print(f"  {line}")
            raise Exception(f"Frontend server process terminated unexpectedly")

        recent_lines = []
        while not output_queue.empty():
            line = output_queue.get()
            recent_lines.append(line)

            if "compiled successfully" in line.lower() or "webpack compiled" in line.lower():
                compiled = True
                print(f"✅ Frontend compiled: {line}")
            elif "failed to compile" in line.lower() or "compilation failed" in line.lower():
                print(f"❌ Frontend compilation failed!")
                print("Recent output before failure:")
                for prev_line in recent_lines[-20:]:
                    print(f"  {prev_line}")
                print(f"Full compilation output saved to: {frontend_log_file}")
                raise Exception(f"Frontend compilation failed - check {frontend_log_file} for details")

        if attempt % 10 == 0 and recent_lines:
            print(f"Recent frontend output (attempt {attempt + 1}/90):")
            for line in recent_lines[-3:]:
                print(f"  {line}")

        if compiled:
            try:
                response = requests.get(frontend_url, timeout=3)
                if response.status_code == 200:
                    print(f"✅ Frontend server is ready on port {port}!")
                    break
            except requests.exceptions.ConnectionError:
                print("Frontend compiled but connection refused...")
            except requests.exceptions.Timeout:
                print("Frontend request timeout...")
            except Exception as e:
                print(f"Frontend connection error: {e}")

        time.sleep(1)
    else:
        print("❌ Frontend server failed to start after 90 seconds")
        remaining_output = []
        while not output_queue.empty():
            remaining_output.append(output_queue.get())
        print("Final frontend output:")
        for line in remaining_output[-20:]:
            print(f"  {line}")
        print(f"Full output saved to: {frontend_log_file}")
        kill_process_tree(process.pid)
        raise Exception(f"Frontend server failed to start - check {frontend_log_file} for full output")

    print(f"✅ Frontend server startup completed successfully on port {port}!")
    yield frontend_url + "/jam"

    # Cleanup
    print(f"Cleaning up frontend server on port {port}...")
    kill_process_tree(process.pid)
    time.sleep(2)
    if kill_process_on_port(port):
        print(f"Found and killed additional process on port {port}")
    print("✅ Frontend server cleanup completed.")
    print(f"Frontend logs saved in: {settings.log_directory}")


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


@contextmanager
def timed_step(label: str, timings: list | None = None):
    """Context manager to time a step and optionally record it."""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"  ⏱ {label}: {elapsed:.3f}s")
    if timings is not None:
        timings.append((label, elapsed))


class BaseUtils(object):
    """Base class for selenium utilities"""

    driver: WebDriver = None
    wait: WebDriverWait = None
    frontend_base_url: str = ""
    backend_base_url: str = ""
    db = None
    client = None

    def go_to_page(self, page) -> None:
        """Helper method to go to a specific page"""

        self.driver.execute_script(f"window.history.pushState({{}}, '', '{self.frontend_base_url}/{page}');")
        self.driver.execute_script("window.dispatchEvent(new Event('popstate'));")
        # self.driver.get(f"{self.frontend_base_url}/{page}")
        self.wait_for_page(page)

    def wait_for_page(self, page_url: str) -> None:
        """Wait for the dashboard to load"""

        url = f"{self.frontend_base_url}/{page_url}"
        try:
            self.wait.until(ec.url_to_be(url))
        except:
            raise AssertionError(f"Failed to wait for URL {url}. Current URL: {self.driver.current_url}")

    def advance_browser_clock_days(self, days: int) -> None:
        self.driver.execute_script(
            """
            const RealDate = window.Date;

            const offsetMs = Number(arguments[0]) || 0;
            const baseTime = RealDate.now() + offsetMs;

            function MockDate(...args) {
                if (this instanceof MockDate) {
                    return args.length
                        ? new RealDate(...args)
                        : new RealDate(baseTime);
                }
                return RealDate();
            }

            MockDate.prototype = RealDate.prototype;

            // Preserve static methods
            MockDate.now = () => baseTime;
            MockDate.parse = RealDate.parse;
            MockDate.UTC = RealDate.UTC;

            window.Date = MockDate;
        """,
            days * 24 * 60 * 60 * 1000,
        )

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
        """Get an element by its ID, with retry on stale element references.
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
            all_ids = self.get_all_element_ids()

            # If element exists in DOM, provide diagnostic info
            if element_id in all_ids:
                element = self.driver.find_element(selector, element_id)
                diagnostics = self._get_element_diagnostics(element)
                raise AssertionError(
                    f"Element '{element_id}' exists in DOM but failed to become clickable.\n"
                    f"Diagnostics:\n{diagnostics}"
                )
            else:
                raise AssertionError(f"Could not find element {element_id}\n" f"Possible IDs: {all_ids}")

    def check_element_exists(
        self,
        element_id: str,
        selector: str = By.ID,
        timeout: float = 0.1,
    ) -> bool:
        """Check if an element exists by its ID.
        :param element_id: ID of the element to check
        :param selector: Selector to use for finding the element
        :param timeout: How long to wait before raising an error"""

        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(ec.presence_of_element_located((selector, element_id)))
            return True
        except TimeoutException:
            return False

    def _get_element_diagnostics(self, element: WebElement) -> str:
        """Get diagnostic information about why an element isn't clickable"""

        diagnostics = []

        # Check visibility
        try:
            is_displayed = element.is_displayed()
            diagnostics.append(f"  - is_displayed(): {is_displayed}")
        except Exception as e:
            diagnostics.append(f"  - is_displayed(): Error - {e}")

        # Check enabled state
        try:
            is_enabled = element.is_enabled()
            diagnostics.append(f"  - is_enabled(): {is_enabled}")
        except Exception as e:
            diagnostics.append(f"  - is_enabled(): Error - {e}")

        # Check CSS properties
        try:
            display = element.value_of_css_property("display")
            visibility = element.value_of_css_property("visibility")
            opacity = element.value_of_css_property("opacity")
            diagnostics.append(f"  - CSS display: {display}")
            diagnostics.append(f"  - CSS visibility: {visibility}")
            diagnostics.append(f"  - CSS opacity: {opacity}")
        except Exception as e:
            diagnostics.append(f"  - CSS properties: Error - {e}")

        # Check position/size
        try:
            size = element.size
            location = element.location
            diagnostics.append(f"  - Size: {size}")
            diagnostics.append(f"  - Location: {location}")
        except Exception as e:
            diagnostics.append(f"  - Size/Location: Error - {e}")

        # Check for overlapping elements
        try:
            overlapping = self._check_overlapping_elements(element)
            if overlapping:
                diagnostics.append(f"  - Overlapping elements detected: {overlapping}")
            else:
                diagnostics.append(f"  - No overlapping elements detected")
        except Exception as e:
            diagnostics.append(f"  - Overlap check: Error - {e}")

        # Check page load state
        try:
            ready_state = self.driver.execute_script("return document.readyState;")
            diagnostics.append(f"  - Page readyState: {ready_state}")
        except Exception as e:
            diagnostics.append(f"  - Page state: Error - {e}")

        return "\n".join(diagnostics)

    def _check_overlapping_elements(self, element: WebElement) -> str:
        """Check if another element is overlaying the target element"""

        try:
            # Get element center point
            location = element.location
            size = element.size
            center_x = location["x"] + size["width"] / 2
            center_y = location["y"] + size["height"] / 2

            # Find element at that point using JavaScript
            script = """
            var element = arguments[0];
            var x = arguments[1];
            var y = arguments[2];
            var topElement = document.elementFromPoint(x, y);
            
            if (topElement === element) {
                return null;
            }
            
            // Return info about the overlapping element
            return {
                tag: topElement.tagName,
                id: topElement.id || 'no-id',
                class: topElement.className || 'no-class',
                zIndex: window.getComputedStyle(topElement).zIndex
            };
            """

            result = self.driver.execute_script(script, element, center_x, center_y)

            if result:
                return f"<{result['tag']} id='{result['id']}' class='{result['class']}' z-index='{result['zIndex']}'>"
            return ""

        except Exception as e:
            return f"Error checking overlap: {e}"

    def wait_for_element_text(
        self,
        element_id: str,
        expected_text: str,
        selector: str = By.ID,
        timeout: float = 10.0,
    ) -> WebElement:
        """Wait for an element's text to become the expected value.
        :param element_id: ID of the element to check
        :param expected_text: The text value to wait for
        :param selector: Selector to use for finding the element
        :param timeout: How long to wait before raising an error
        :return: The element once its text matches"""

        def text_matches(driver):
            try:
                el = driver.find_element(selector, element_id)
                return el if el.text == expected_text else False
            except:
                return False

        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(text_matches)
        except TimeoutException:
            # Get actual text for error message
            try:
                element = self.driver.find_element(selector, element_id)
                actual_text = element.text
            except:
                actual_text = "<element not found>"
            raise AssertionError(
                f"Element '{element_id}' text did not become '{expected_text}' within {timeout}s. "
                f"Actual text: '{actual_text}'"
            )

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

    def context_menu(self, element: WebElement, choice: str) -> None:
        """Row context menu"""

        actions = ActionChains(self.driver)
        actions.context_click(element).perform()
        self.get_element(f"context-menu-{choice}").click()

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

    def get_verification_link_from_email(self, email: str) -> str:
        """Helper method to get verification link from test email endpoint"""

        response = requests.get(f"{self.backend_base_url}/test/verification-link/{email}")
        assert response.status_code == 200, f"Failed to get verification link: {response.text}"
        return response.json()["verification_url"]

    def get_reset_link_from_email(self, email: str) -> str:
        """Helper method to get password reset link from test email endpoint"""

        response = requests.get(f"{self.backend_base_url}/test/reset-link/{email}")
        assert response.status_code == 200, f"Failed to get reset link: {response.text}"
        return response.json()["reset_url"]

    def clear_test_emails(self) -> None:
        """Helper method to clear all test emails"""

        response = requests.delete(f"{self.backend_base_url}/test/emails")
        assert response.status_code == 200, "Failed to clear test emails"

    # ---------------------------------------------------- ELEMENTS ----------------------------------------------------

    def wait_for_delete_modal(self) -> WebElement:
        """Wait for the delete modal to appear"""

        return self.get_element("delete-alert-modal")

    @property
    def toast(self) -> WebElement:
        """Get the toast modal on the modal"""

        return self.get_element("toast")

    def assert_toast_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        element = self.toast
        assert error_message in element.text, f"Message not found: {error_message}"
        element.click()  # Dismiss toast

    def wait_for_windows(self, n: int) -> None:
        """Wait for the given number of browser windows to be present"""

        self.wait.until(ec.number_of_windows_to_be(n))

    def switch_to_window(self, index: int) -> None:
        """Switch to the browser window with the given index"""

        self.driver.switch_to.window(self.driver.window_handles[index])


class BaseUtilsClass(BaseUtils):

    def __init__(self, driver: WebDriver, frontend_base_url, backend_base_url, db, client):
        """Object constructor
        :param driver: Selenium WebDriver instance
        :param frontend_base_url: Base URL of the frontend server
        :param backend_base_url: Base URL of the backend server
        :param db: Database session for backend API calls"""

        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.frontend_base_url = frontend_base_url
        self.backend_base_url = backend_base_url
        self.db = db
        self.client = client


def format_field(label: str | None, value: str | None) -> str:
    """Format a field for display in a view modal, showing 'Not Provided' for None values.
    :param label: The field label to display
    :param value: The value to display, or None
    :return: Formatted string with label and value or 'Not Provided'"""

    if label:
        return f"{label}\n{value if value else 'Not Provided'}\n"
    else:
        return f"{value if value else 'Not Provided'}\n"


class DataModalUtils(BaseUtilsClass):
    """Base class for testing data modals"""

    def __init__(self, entry_type: str, **kwargs):
        """Object constructor
        :param entry_type: Type of entry (e.g., "job", "company", etc.)
        :param kwargs: Additional arguments for the base class"""

        BaseUtilsClass.__init__(self, **kwargs)
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

    def wait_for_import_modal(self) -> WebElement:
        """Wait for the import modal to close"""

        return self.get_element(f"modal-import-{self.entry_type}")

    def wait_for_import_modal_close(self) -> None:
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

    def _fill_modal(self, duplicate_fields=None, **values) -> None:
        """Fill the modal with the given values (key: key of the input elements, value: value to set)."""

        if any(isinstance(v, dict) for v in values.values()):
            for tab_key in values:
                self.get_element(f"{tab_key}-tab").click()
                self._fill_modal(**values[tab_key])
        else:
            self.wait_for_edit_modal()
            for key, value in values.items():
                if duplicate_fields and key not in duplicate_fields:
                    continue
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
                    select.select_by_visible_text(value)
                elif key in ["date", "application_date"]:
                    self.get_element(key + "_set_current").click()
                else:
                    self.set_text(self.get_element(key), value)

    def check_edit_modal(self, **values) -> None:
        """Check that the modal in edit mode contains the expected data
        :param values: values to check"""

        if any(isinstance(v, dict) for v in values.values()):
            for tab_key in values:
                self.get_element(f"{tab_key}-tab").click()
                self.check_edit_modal(**values[tab_key])
        else:
            for key in values:
                if "date" in key:
                    continue
                element = self.get_element(key)
                if element.tag_name == "input":
                    value = element.get_attribute("value")
                else:
                    value = element.text
                assert str(value) == str(values[key])

    # -------------------------------------------------- VIEW MODALS --------------------------------------------------

    def test_view_modal(self, entry=None) -> None:
        """Helper method to test the view modal for an entry"""

        if self.entry_type == "keyword":
            self.check_keyword_view_modal(entry)
        elif self.entry_type == "aggregator":
            self.check_aggregator_view_modal(entry)
        elif self.entry_type == "company":
            self.check_company_view_modal(entry)
        elif self.entry_type == "location":
            self.check_location_view_modal(entry)
        elif self.entry_type == "person":
            self.check_person_view_modal(entry)
        elif self.entry_type == "jobApplicationUpdate":
            self.check_update_view_modal(entry)
        elif self.entry_type == "interview":
            self.check_interview_view_modal(entry)
        elif self.entry_type == "job":
            self.check_job_view_modal(entry)
        elif self.entry_type == "speculativeApplication":
            self.check_speculative_application_view_modal(entry)
        elif self.entry_type == "setting":
            self.check_setting_view_modal(entry)
        else:
            raise AssertionError("Not implemented")

    def check_keyword_view_modal(self, entry: models.Keyword) -> None:
        """Helper method to test the view modal for a keyword entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        expected = f"Tag Details\n{entry.name}\n"
        if entry.jobs:
            expected += f"Jobs\n({len(entry.jobs)})\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_aggregator_view_modal(self, entry: models.Aggregator) -> None:
        """Helper method to test the view modal for an aggregator entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        expected = f"Aggregator Details\n{entry.name}\nWebsite\n{entry.url.replace('https://', '')}\n"
        if entry.jobs:
            expected += f"Jobs\n({len(entry.jobs)})\n"
        if entry.job_applications:
            expected += f"Job Applications\n({len(entry.job_applications)})\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_location_view_modal(self, entry: models.Location) -> None:
        """Helper method to test the view modal for a location entry"""

        modal = self.wait_for_view_modal()
        WebDriverWait(self.driver, 30).until(lambda d: "Finding location on map..." not in modal.text)
        if (
            "No mappable locations found" in modal.text
            or "This location could not be found" in modal.text
            or "An error occurred when trying to locate this entry" in modal.text
        ):
            return

        # Verify modal contains the entry information
        expected = (
            f"Location Details\nCity\n{entry.city}\nPostcode\n{entry.postcode}"
            f"\nCountry\n{entry.country}\n"
            f"Location on Map\n+\n−\nLeaflet | © OpenStreetMap contributors © CARTO\n"
        )
        if entry.jobs:
            expected += f"Jobs\n({len(entry.jobs)})\n"
        if entry.interviews:
            expected += f"Interviews\n({len(entry.interviews)})\n"
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()
        return

    def check_company_view_modal(self, entry: models.Company) -> None:
        """Helper method to test the view modal for a company entry"""

        modal = self.wait_for_view_modal()

        # Verify modal contains the entry information
        expected = (
            f"Company Details\n{entry.name}\nWebsite\n{entry.url.replace("https://", "")}"
            f"\nDescription\n{entry.description}\n"
        )
        if entry.jobs:
            expected += f"Jobs\n({len(entry.jobs)})\n"
        if entry.persons:
            expected += f"Persons\n({len(entry.persons)})\n"
        expected += "Close\nEdit"
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
        )
        if entry.interviews:
            expected += f"Interviews\n({len(entry.interviews)})\n"
        if entry.jobs:
            expected += f"Jobs\n({len(entry.jobs)})\n"
        if entry.recruited_jobs:
            expected += f"Recruited Jobs\n({len(entry.recruited_jobs)})\n"
        expected += "Close\nEdit"
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
        entry_type = {"HR": "HR", "Technical": "Technical"}[entry.type]
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
            expected += format_field("Location", None)

        interviewers = (
            ", ".join([interviewer.name.upper() for interviewer in entry.interviewers]) if entry.interviewers else None
        )
        expected += format_field("Interviewers", interviewers)

        expected += format_field("Notes", entry.note)

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
            )
        else:
            expected = (
                "Job Application Update Details\n"
                "Date & Time\n"
                f"{display_time.strftime("%d/%m/%Y %H:%M")}\n"
                "Type\n"
                f"{entry.type[0].upper() + entry.type[1:]}\n"
            )
        expected += format_field("Notes", entry.note)
        expected += "Close\nEdit"
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
        expected += "\nOverview"
        expected += f"\n{entry.title}\n"

        company = entry.company.name.upper() if entry.company else None
        expected += format_field("Company", company)

        if entry.attendance_type and not entry.location:
            expected += f"Location\n{entry.attendance_type.upper()}\n"
        elif entry.attendance_type and entry.location:
            expected += f"Location\n{entry.location.name.upper()} ({entry.attendance_type.upper()})\n"
        elif not entry.attendance_type and entry.location:
            expected += f"Location\n{entry.location.name.upper()}\n"
        else:
            expected += format_field("Location", None)

        expected += "Details\n"
        expected += format_field("Description", entry.description)
        expected += format_field("Notes", entry.note)

        expected += "Compensation & Priority\n"
        expected += format_field("Salary Range", self.salary_range(entry))

        expected += "Personal Rating\n"
        if not entry.personal_rating:
            expected += "Not Provided\n"

        deadline = entry.deadline.strftime("%d/%m/%Y") if entry.deadline else None
        expected += format_field("Application Deadline", deadline)

        expected += "Source & Links\n"
        if entry.source_type in ["aggregator", "aggregator_email"]:
            expected += format_field(
                "Source Aggregator", entry.source_aggregator.name.upper() if entry.source_aggregator else None
            )
        elif entry.source_type == "recruiter":
            expected += format_field("Source Recruiter", entry.recruiter.name.upper() if entry.recruiter else None)
        elif entry.source_type == "recruitment_company":
            expected += format_field(
                "Source Recruitment Company",
                entry.recruitment_company.name.upper() if entry.recruitment_company else None,
            )
        else:
            expected += format_field("Source", entry.source_type.capitalize() if entry.source_type else None)

        url = entry.url.replace("https://", "") if entry.url else None
        expected += format_field("Job URL", url)

        expected += "Tags & Contacts\n"
        if entry.keywords:
            tags = "\n".join([tag.name.upper() for tag in entry.keywords])
            expected += format_field("Tags", tags)

        if entry.contacts:
            contacts = "\n".join([person.name.upper() for person in entry.contacts])
            expected += format_field("Contacts", contacts)

        expected += "Close\nEdit"
        assert modal.text == expected

        # Job Application
        self.get_element("application-tab").click()
        expected = "Job Details\nJob Details\n"
        if entry.application_status:
            expected += f"Job Application {entry.application_status.upper()}\n"
        else:
            expected += "Job Application\n"
        expected += "Application Details\n"
        app_date = entry.application_date.astimezone().strftime("%d/%m/%Y") if entry.application_date else None
        expected += format_field("Application Date" if entry.application_date else "Date", app_date)

        app_status = entry.application_status.upper() if entry.application_status else None
        expected += format_field("Status", app_status)

        if entry.applied_via == "aggregator" and entry.application_aggregator:
            applied_via = entry.application_aggregator.name.upper()
        elif entry.applied_via:
            applied_via = entry.applied_via.upper()
        else:
            applied_via = None
        expected += format_field("Applied Via", applied_via)

        app_url = entry.application_url.replace("https://", "") if entry.application_url else None
        expected += format_field("Application URL", app_url)

        expected += "Notes\n"
        expected += format_field(None, entry.application_note if entry.note else None)
        expected += (
            "Add Interview\n"
            "Date\n"
            "Type\n"
            "Location\n"
            "Notes\n"
            "No Interviews found\n"
            "Add Job Application Update\n"
            "Date\n"
            "Type\n"
            "Notes\n"
            "No Job Application Updates found\n"
        )
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_speculative_application_view_modal(self, entry: models.SpeculativeApplication) -> None:
        """Helper method to test the view modal for a speculative application entry"""

        modal = self.wait_for_view_modal()
        expected = "Speculative Application Details\n" "Company\n" f"{entry.company.name.upper()}\n"

        date_time = entry.date.astimezone().strftime("%d/%m/%Y %H:%M") if entry.date else None
        expected += format_field("Date & Time", date_time)

        expected += format_field("Contact Email", entry.contact_email)

        if entry.contacts:
            contacts = "\n".join([person.name.upper() for person in entry.contacts])
            expected += format_field("Contacts", contacts)
        else:
            expected += format_field("Contacts", None)

        expected += format_field("Notes", entry.note)
        expected += "Close\nEdit"
        assert modal.text == expected

        # Close modal
        self.cancel_button("view").click()
        self.wait_for_view_modal_close()

    def check_setting_view_modal(self, entry: models.Setting):
        """Helper method to test the view modal for a settings entry"""

        modal = self.wait_for_view_modal()
        expected = f"Setting Details\n" f"Name\n{entry.name}\n" f"Value\n{entry.value}\n"
        expected += format_field("Description", entry.description)
        expected += f"Active\n" f"Close\nEdit"
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

    def __init__(self, entry_type: str, **kwargs):
        """Object constructor
        :param entry_type: Type of entry (e.g., "job", "company", etc.)
        :param kwargs: Additional arguments for the base class"""

        BaseUtilsClass.__init__(self, **kwargs)
        self.entry_type = entry_type

    # ----------------------------------------------------- TABLES -----------------------------------------------------

    @property
    def table_rows(self) -> list[WebElement]:
        """Get all table rows on the page"""

        time.sleep(0.5)
        try:
            self.get_element(f"[id^='table-row-{self.entry_type}-']", By.CSS_SELECTOR, 1)
        except AssertionError:
            return []
        return self.driver.find_elements(By.CSS_SELECTOR, f"[id^='table-row-{self.entry_type}-']")

    def table_row(self, item_id: int, *args, **kwargs) -> WebElement:
        """Get a specific table row by its ID"""

        return self.get_element(f"table-row-{self.entry_type}-{item_id}", *args, **kwargs)

    def table_context_menu(self, entity_id: int, choice: str) -> None:
        """Row context menu"""

        self.context_menu(self.table_row(entity_id), choice)

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

    def check_id_in_table(self, entry_id: int, **kwargs) -> bool:
        """Check if an ID is in the table"""

        try:
            self.get_element(f"[id^='table-row-{self.entry_type}-']", By.CSS_SELECTOR, **kwargs)
        except AssertionError:
            return False
        rows = self.driver.find_elements(By.CSS_SELECTOR, f"[id^='table-row-{self.entry_type}-']")
        return any(row.get_attribute("id") == f"table-row-{self.entry_type}-{entry_id}" for row in rows)

    def check_id_not_in_table(self, entry_id: int) -> bool:
        """Check if an ID is not in the table"""

        return not self.check_id_in_table(entry_id, timeout=2)

    def set_search(self, search_text: str) -> None:
        """Set the search input to the given text"""

        self.set_text(self.get_element("search-input"), search_text)
        time.sleep(0.2)

    # ----------------------------------------------------- BUTTONS ----------------------------------------------------

    @property
    def add_entity_button(self) -> WebElement:
        """Get the Add Entity button"""

        return self.get_element(f"add-{self.entry_type}-button")

    @property
    def deadline_toggle(self) -> WebElement:
        """Get the Deadline Toggle button"""

        return self.get_element("show-past-deadline-toggle")

    def set_page_item_select(self, value: str) -> None:
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

        self.go_to_page(f"login")

    def go_to_register(self) -> None:
        """Go to the register page"""

        self.go_to_page(f"register")
        time.sleep(0.5)  # animation

    def go_to_forgot_password(self) -> None:
        """Go to the forgot password page"""

        self.go_to_page(f"forgot-password")
        time.sleep(0.5)  # animation

    @property
    def try_button(self) -> WebElement:
        """Get the Try button"""

        return self.get_element("try-app-btn")

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
        time.sleep(0.5)

    def go_to_verification_url(self, token: str) -> None:
        """Navigate to login page with verification token"""

        self.driver.get(f"{self.frontend_base_url}/verify-email/?token={token}")

    def switch_to_forgot_password(self) -> None:
        """Navigate to forgot password page"""

        self.get_element("forgot-password-link").click()
        time.sleep(0.5)


class UserSettingsUtils(BaseUtilsClass):
    """Test class for the User Settings Page"""

    def go_to_account_tab(self) -> None:
        """Get the account tab button"""

        self.get_element("account-tab").click()

    def go_to_preferences_tab(self) -> None:
        """Get the preferences tab button"""

        self.get_element("preferences-tab").click()

    def go_to_qualifications_tab(self) -> None:
        """Get the qualifications tab button"""

        self.get_element("qualifications-tab").click()

    def go_to_premium_tab(self) -> None:
        """Get the premium tab button"""

        self.get_element("premium-tab").click()

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

    @property
    def currency(self) -> ReactSelect:
        """Get the currency field"""

        return ReactSelect(self.get_element("default_currency"))

    def get_theme(self, theme_key: str) -> WebElement:
        """Get the theme field"""

        return self.get_element(theme_key + "-theme")

    @property
    def dark_mode_btn(self) -> WebElement:
        """Get the dark mode toggle button"""

        return self.get_element("theme-dark-btn")

    @property
    def light_mode_btn(self) -> WebElement:
        """Get the light mode toggle button"""

        return self.get_element("theme-light-btn")

    @property
    def system_theme_btn(self) -> WebElement:
        """Get the system theme toggle button"""

        return self.get_element("theme-system-btn")

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

    @property
    def download_data_button(self) -> WebElement:
        """Get the download data button"""

        return self.get_element("download-data-button")

    @property
    def delete_account_button(self) -> WebElement:
        """Get the delete account button"""

        return self.get_element("delete-account-button")

    @property
    def delete_password(self) -> WebElement:
        """Get the delete password field"""

        return self.get_element("delete_password")

    @property
    def delete_account_modal(self) -> WebElement:
        """Get the delete account modal"""

        return self.get_element("delete-account-modal")

    @property
    def cancel_delete_button(self) -> WebElement:
        """Get the cancel delete button in first modal"""

        return self.get_element("cancel-delete-button")

    @property
    def continue_delete_button(self) -> WebElement:
        """Get the continue button in first modal"""

        return self.get_element("continue-delete-button")

    @property
    def confirm_delete_modal(self) -> WebElement:
        """Get the confirmation delete modal"""

        return self.get_element("confirm-delete-modal")

    @property
    def download_data_modal_button(self) -> WebElement:
        """Get the download data button in confirmation modal"""

        return self.get_element("download-data-modal-button")

    @property
    def cancel_confirm_delete_button(self) -> WebElement:
        """Get the cancel button in confirmation modal"""

        return self.get_element("cancel-confirm-delete-button")

    @property
    def final_delete_button(self) -> WebElement:
        """Get the final delete button"""

        return self.get_element("final-delete-button")

    @property
    def experience_input(self) -> WebElement:
        """Get the experience input field"""

        return self.get_element("experience")

    @property
    def skills_input(self) -> WebElement:
        """Get the skills input field"""

        return self.get_element("skills")

    @property
    def qualities_input(self) -> WebElement:
        """Get the qualities input field"""

        return self.get_element("qualities")

    @property
    def education_input(self) -> WebElement:
        """Get the education input field"""

        return self.get_element("education")

    @property
    def interests_input(self) -> WebElement:
        """Get the interests input field"""

        return self.get_element("interests")


class FollowUpEmailModalUtils(BaseUtilsClass):
    """Utilities for the Follow-Up Email Modal."""

    def wait_for_modal(self) -> WebElement:
        """Get the follow-up email modal element."""

        return self.get_element("follow-up-modal")

    def wait_for_modal_close(self) -> None:
        """Wait for the follow-up email modal to close."""

        self._wait_for_modal_close("follow-up-modal")

    @property
    def contact(self) -> ReactSelect:
        """Get the contact element in the modal."""

        return ReactSelect(self.get_element("contactId"))

    @property
    def contact_text(self) -> str:
        """Get the contact text element in the modal."""

        return self.get_element("contactId").text

    @property
    def subject(self) -> WebElement:
        """Get the subject element in the modal."""

        return self.get_element("subject")

    @property
    def body(self) -> WebElement:
        """Get the body element in the modal."""

        return self.get_element("body")

    @property
    def cancel_button(self) -> WebElement:
        """Get the cancel button in the modal."""

        return self.get_element("cancel-btn")

    @property
    def send_button(self) -> WebElement:
        """Get the send button in the modal."""

        return self.get_element("send-btn")

    @property
    def send_menu_button(self) -> WebElement:
        """Get the send button in the modal."""

        return self.get_element("dropdown-split-email")

    @property
    def gmail_option(self) -> WebElement:
        """Get the Gmail option in the send menu."""

        return self.get_element("gmail-btn")

    @property
    def outlook_option(self) -> WebElement:
        """Get the Outlook option in the send menu."""

        return self.get_element("outlook-btn")

    @property
    def default_option(self) -> WebElement:
        """Get the Yahoo option in the send menu."""

        return self.get_element("default-email-btn")


class AlertModalUtils(BaseUtilsClass):
    """Utilities for the Confirm Modal."""

    key = ""

    def wait_for_modal(self) -> WebElement:
        """Get the confirm modal element."""

        return self.get_element(f"{self.key}-alert-modal")

    def wait_for_modal_close(self) -> None:
        """Wait for the confirm modal to close."""

        self._wait_for_modal_close(f"{self.key}-alert-modal")

    @property
    def confirm_button(self) -> WebElement:
        """Get the confirm button in the modal."""

        return self.get_element(f"{self.key}-alert-modal-confirm-button")

    @property
    def cancel_button(self) -> WebElement:
        """Get the cancel button in the modal."""

        return self.get_element(f"{self.key}-alert-modal-cancel-button")


class ConfirmModalUtils(AlertModalUtils):
    """Utilities for the Confirm Modal."""

    key = "confirm"


class DeleteModalUtils(AlertModalUtils):
    """Utilities for the Delete Modal."""

    key = "delete"


class PremiumSettingsUtils(BaseUtilsClass):

    @property
    def confirmation_link_alert(self) -> WebElement:
        return self.get_element("confirmation-link-alert")

    @property
    def confirmation_link_heading(self) -> WebElement:
        return self.get_element("confirmation-link-heading")

    @property
    def confirmation_link_prompt(self) -> WebElement:
        return self.get_element("confirmation-link-prompt")

    @property
    def confirmation_link_confirm_button(self) -> WebElement:
        return self.get_element("confirmation-link-prompt-confirm-button")

    @property
    def confirmation_link_cancel_button(self) -> WebElement:
        return self.get_element("confirmation-link-prompt-cancel-button")

    def dismiss_confirmation_link_alert(self) -> None:
        """Dismiss the warning alert to trigger the showConfirm prompt."""

        self.confirmation_link_alert.find_element(By.CSS_SELECTOR, ".btn-close").click()
        time.sleep(0.5)

    def delete_stripe_data(self) -> None:
        """Delete Stripe customer data for the user"""

        response = self.client.delete("/test/delete-all-customers")
        assert response.status_code == 200

    def advance_clock(self, days: int = 15) -> None:
        """Advance the Stripe clock"""

        response = self.client.post("/test/advance-test-clock", json={"days": days})
        assert response.status_code == 200
        self.advance_browser_clock_days(days)

    @property
    def subscription_button(self) -> WebElement:
        """Subscribe button element"""

        return self.get_element("subscription-button")

    def assert_status_title(self, expected_title: str) -> None:
        """Assert status title"""

        assert self.wait_for_element_text("status-title", expected_title)

    def assert_status_message(self, expected_message: str) -> None:
        """Assert status message"""

        assert self.wait_for_element_text("status-message", expected_message)

    @property
    def stripe_add_payment_method_button(self) -> WebElement:
        """Add payment method button element"""

        return self.get_element("[data-test='add-payment-method']", By.CSS_SELECTOR)

    @property
    def stripe_cancel_subscription_button(self) -> WebElement:
        """Cancel subscription button element"""

        return self.get_element("[data-test='cancel-subscription']", By.CSS_SELECTOR)

    @property
    def stripe_return_to_business_link(self) -> WebElement:
        """Return to business link element"""

        return self.get_element("[data-testid='return-to-business-link']", By.CSS_SELECTOR)

    @property
    def stripe_start_trial_button(self) -> WebElement:
        """Start trial button element"""

        return self.get_element("[data-testid='hosted-payment-submit-button']", By.CSS_SELECTOR)

    @property
    def stripe_confirm_button(self) -> WebElement:
        """Confirm button element"""

        return self.get_element("[data-test='confirm']", By.CSS_SELECTOR)

    @property
    def stripe_cancel_feedback(self) -> WebElement:
        """Confirm button element"""

        return self.get_element("[data-testid='cancellation_reason_cancel']", By.CSS_SELECTOR)

    def set_stripe_payment_details(self) -> None:
        """Set payment details in the Stripe iframe"""

        self.driver.switch_to.frame(0)
        self.get_element("card-tab").click()
        self.set_text(self.get_element("payment-numberInput"), "4242 4242 4242 4242")
        self.set_text(self.get_element("payment-cvcInput"), "123")
        self.get_element("payment-countryInput", timeout=2).send_keys("United States")
        self.set_text(self.get_element("payment-expiryInput"), "1228")
        self.set_text(self.get_element("payment-postalCodeInput"), "10001")
        self.driver.switch_to.default_content()
        self.stripe_confirm_button.click()
        time.sleep(3)


class BaseTest(BaseUtils):
    """Base class for selenium tests"""

    _shared_backend_url = None
    _shared_frontend_url = None
    _shared_driver = None
    user = None  # user to use
    client = None  # authorised client
    base_utils = None  # base utils

    # Parameters needed
    page_url = "dashboard"  # url of the page to test (not including the base url)
    user_index = 1  # index of the user to use for the test

    _test_name = ""

    # Company
    company_modal_utils: DataModalUtils = None
    company_table_utils: DataTableUtils = None

    # Aggregator
    aggregator_modal_utils: DataModalUtils = None
    aggregator_table_utils: DataTableUtils = None

    # Keyword
    keyword_modal_utils: DataModalUtils = None
    keyword_table_utils: DataTableUtils = None

    # Location
    location_modal_utils: DataModalUtils = None
    location_table_utils: DataTableUtils = None

    # Person
    person_modal_utils: DataModalUtils = None
    person_table_utils: DataTableUtils = None

    # Job
    job_modal_utils: DataModalUtils = None
    job_table_utils: DataTableUtils = None

    # Interview
    interview_modal_utils: DataModalUtils = None
    interview_table_utils: DataTableUtils = None

    # Job Application Update
    jobApplicationUpdate_modal_utils: DataModalUtils = None
    jobApplicationUpdate_table_utils: DataTableUtils = None

    # Speculative Application
    speculativeApplication_modal_utils: DataModalUtils = None
    speculativeApplication_table_utils: DataTableUtils = None

    # Scraped Job
    scrapedJob_modal_utils: DataModalUtils = None
    scrapedJob_table_utils: DataTableUtils = None

    # Scraping Filter
    scrapingFilter_modal_utils: DataModalUtils = None
    scrapingFilter_table_utils: DataTableUtils = None

    # Settings
    setting_modal_utils: DataModalUtils = None
    setting_table_utils: DataTableUtils = None

    # Others
    auth_utils: AuthentificationUtils = None
    user_settings_utils: UserSettingsUtils = None
    followup_modal: FollowUpEmailModalUtils = None
    confirm_modal: ConfirmModalUtils = None
    delete_modal: DeleteModalUtils = None
    premium_settings_utils: PremiumSettingsUtils = None

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
                "protocol_handler": {"excluded_schemes": {"mailto": True}},
                "intl.accept_languages": "en-GB",
            }
            chrome_options.add_experimental_option("prefs", prefs)
            # chrome_options.add_argument("--headless=new")
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
            self.wait = WebDriverWait(self.driver, 10)

            # Set timezone using CDP
            self.driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": "Europe/London"})
            # Set locale using CDP
            self.driver.execute_cdp_cmd("Emulation.setLocaleOverride", {"locale": "en-GB"})

            # Frontend/Backend
            self.frontend_base_url = test_frontend_server
            self.backend_base_url = test_backend_server

            # Client/User
            self.user = test_users[self.user_index]
            self.client = authorised_clients[self.user_index]
            self.db = session

            modal_entities = [
                "company",
                "aggregator",
                "keyword",
                "location",
                "person",
                "job",
                "interview",
                "jobApplicationUpdate",
                "speculativeApplication",
                "scrapedJob",
                "scrapingFilter",
                "setting",
            ]

            shared_kwargs = {
                "driver": self.driver,
                "frontend_base_url": self.frontend_base_url,
                "backend_base_url": self.backend_base_url,
                "db": self.db,
                "client": self.client,
            }
            for name in modal_entities:
                setattr(self, f"{name}_modal_utils", DataModalUtils(entry_type=name, **shared_kwargs))
            for name in modal_entities:
                setattr(self, f"{name}_table_utils", DataTableUtils(entry_type=name, **shared_kwargs))

            self.auth_utils = AuthentificationUtils(**shared_kwargs)
            self.user_settings_utils = UserSettingsUtils(**shared_kwargs)
            self.followup_modal = FollowUpEmailModalUtils(**shared_kwargs)
            self.confirm_modal = ConfirmModalUtils(**shared_kwargs)
            self.delete_modal = DeleteModalUtils(**shared_kwargs)
            self.premium_settings_utils = PremiumSettingsUtils(**shared_kwargs)

            self.driver.get(self.frontend_base_url)
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
            browser_log_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}_browser.log"
            with open(browser_log_file, "w") as f:
                f.write(f"Test: {self._test_name}\n")
                f.write(f"Status: {status_string}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"URL: {self.driver.current_url}\n")
                f.write("=" * 80 + "\n\n")

                for entry in browser_logs:
                    f.write(f"[{entry['level']}] {entry['timestamp']}: {entry['message']}\n")

            # Save performance logs (network requests)
            perf_log_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}_network.log"
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

            screenshot_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}.png"
            self.driver.save_screenshot(str(screenshot_file))
            print(f"✅ Saved screenshot to {screenshot_file}")

        except Exception as e:
            print(f"⚠️ Could not save screenshot: {e}")

    def login(self) -> None:
        """Log in by generating a JWT token directly and injecting it into localStorage."""

        # Generate JWT directly — no HTTP call, no bcrypt verification
        token = create_access_token(
            data={"user_id": self.user.id},
            token_version=self.user.token_version,
        )

        # Inject token into localStorage — browser is already on the same origin from setup_method
        self.driver.execute_script(f'window.localStorage.setItem("token", "{token}");')

        self.driver.get(f"{self.frontend_base_url}/{self.page_url}")
        self.wait_for_page(self.page_url)
        self.wait_for_disappear("loading-spinner")

    # ---------------------------------------------------- DATABASE ----------------------------------------------------

    @property
    def db_user(self) -> models.User:
        """Get the user from the database"""

        self.db.expire_all()
        return self.db.query(models.User).filter(models.User.id == self.user.id).first()

    def verify_user_in_database(self, email: str) -> list[models.User]:
        """Helper method to verify user exists in database"""

        return self.db.query(models.User).filter(models.User.email == email).all()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> Generator[None, Any, None]:
    """Attach test failure information to the request node."""
    _ = call
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


def _save_page_screenshot(self, failed: bool = False) -> None:
    """Save screenshot and page source of current page"""
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        status_string = "FAILED" if failed else "PASSED"
        safe_test_name = self._test_name.replace("/", "_").replace(":", "_")

        # Save screenshot
        screenshot_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}.png"
        self.driver.save_screenshot(str(screenshot_file))
        print(f"✅ Saved screenshot to {screenshot_file}")

        # Save page HTML source
        html_file = settings.log_directory + f"/{safe_test_name}_{status_string}_{timestamp}.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print(f"✅ Saved page source to {html_file}")

    except Exception as e:
        print(f"⚠️ Could not save screenshot/page source: {e}")
