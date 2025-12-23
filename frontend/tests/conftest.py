"""Fixtures and helper functions for integration tests"""

import json
import os
import platform
import queue
import shutil
import subprocess
import threading
from pathlib import Path

import psutil
import requests
import sys
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.webdriver import WebDriver

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


@pytest.fixture(scope="session")
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


def get_all_element_ids(driver) -> list[str]:
    """Get all element IDs present on the current page
    :param driver: Selenium WebDriver instance"""

    # Find all elements that have an ID attribute
    elements_with_id = driver.find_elements(By.XPATH, "//*[@id]")

    # Extract the ID values
    element_ids = []
    for element in elements_with_id:
        element_id = element.get_attribute("id")
        if element_id:
            element_ids.append(element_id)

    return sorted(element_ids)


def get_element(
    driver: WebDriver,
    element_id: str,
    selector: str = By.ID,
    timeout: float = 10.0,
) -> WebElement:
    """Get an element by its ID.
    :param driver: Selenium WebDriver instance
    :param element_id: ID of the element to get
    :param selector: Selector to use for finding the element
    :param timeout: How long to wait before raising an error"""

    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(ec.element_to_be_clickable((selector, element_id)))
        ActionChains(driver).move_to_element(element).perform()
        return element
    except Exception:
        raise AssertionError(f"Could not find element {element_id}\nPossible IDs: {get_all_element_ids(driver)}")


LOGS_DIR = Path(os.path.join(os.path.dirname(settings.log_directory), "test_logs"))
LOGS_DIR.mkdir(exist_ok=True)


class BaseTest:
    """Base class for selenium tests"""

    driver = None  # chrome driver
    wait = None  # chrome driver wait
    frontend_base_url = ""  # frontend base url
    backend_url = ""  # backend url
    user = None  # user to use
    client = None  # client for the current user
    db = None  # database session

    # Parameters needed
    page_url = ""  # url of the page to test (not including the base url)
    user_index = 1  # index of the user to use for the test

    _test_name = ""

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

            self.driver = webdriver.Chrome(options=chrome_options)
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

            self.setup_function(request)

        except Exception:
            if hasattr(self, "driver"):
                try:
                    # self._save_browser_logs(failed=True)
                    self.driver.quit()
                except:
                    pass
            raise
        yield  # This allows the test to run

        # Teardown
        try:
            if hasattr(self, "driver"):
                # Check if test failed
                # test_failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
                #
                # # Save logs on failure or in CI (always in CI for debugging)
                # if test_failed or os.getenv("CI"):
                #     self._save_browser_logs(failed=test_failed)
                #     self._save_page_screenshot(failed=test_failed)
                self.driver.quit()
        except Exception as e:
            print(f"Error during teardown: {e}")

    def setup_function(self, request) -> None:
        """Function to run before each test - can be overridden in subclasses"""
        pass

    def go_to(self, page) -> None:
        """Helper method to go to a specific page"""

        self.driver.get(f"{self.frontend_base_url}/{page}")
        self.wait_for_page(page)

    def login(self) -> None:
        """Helper method to log in to the application"""

        login_url = f"{self.frontend_base_url}/login"
        self.driver.get(login_url)
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
        self.wait_for_table_load()

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

    # ------------------------------------------------ GET/WAIT ELEMENTS -----------------------------------------------

    def wait_for_page(self, page_url: str) -> None:
        """Wait for the dashboard to load"""

        self.wait.until(ec.url_to_be(f"{self.frontend_base_url}/{page_url}"))

    def wait_for_table_load(self, timeout: int | float = 0.1) -> None:
        """Wait for loading spinner to disappear"""

        try:
            WebDriverWait(self.driver, timeout).until(
                ec.invisibility_of_element_located((By.CSS_SELECTOR, "spinner-border"))
            )
        except TimeoutException:
            pass

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
    ) -> WebElement:
        """Get an element by its ID.
        :param element_id: ID of the element to get
        :param selector: Selector to use for finding the element
        :param timeout: How long to wait before raising an error
        """

        time.sleep(0.1)
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(ec.element_to_be_clickable((selector, element_id)))
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

    # ---------------------------------------------------- UTILITIES ---------------------------------------------------

    def _wait_for_modal_close(self, name: str) -> None:
        """Wait for the modal to close"""

        self.wait.until(ec.invisibility_of_element_located((By.ID, name)))

    @property
    def db_user(self) -> models.User:
        """Get the user from the database"""

        self.db.expire_all()
        return self.db.query(models.User).filter(models.User.id == self.user.id).first()

    def verify_user_in_database(self, email: str) -> list[models.User]:
        """Helper method to verify user exists in database"""

        return self.db.query(models.User).filter(models.User.email == email).all()

    def get_verification_token_from_db(self, email: str) -> str:
        """Helper method to get verification token from database"""

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

    def assert_toast_message(self, error_message: str) -> None:
        """Assert that the given error message is displayed on the page"""

        assert error_message in self.get_element("toast").text, f"Message not found: {error_message}"
