"""Fixtures and helper functions for integration tests"""

import itertools
import json
import os
import platform
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
from typing import Optional

import psutil
import requests
from selenium.webdriver import Keys, ActionChains

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
)
from tests.conftest import *


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


def check_backend_health(api_url: str, detailed: bool = True) -> dict:
    """Check backend health and return detailed status information
    :param api_url: Base URL of the API
    :param detailed: Whether to return detailed information
    :return: Dictionary with health check results
    """

    health_info = {
        "status": "unknown",
        "endpoint_accessible": False,
        "response_time_ms": None,
        "status_code": None,
        "response_body": None,
        "error": None,
    }

    try:
        start_time = time.time()
        response = requests.get(f"{api_url}/health", timeout=5)
        end_time = time.time()

        health_info["endpoint_accessible"] = True
        health_info["status_code"] = response.status_code
        health_info["response_time_ms"] = round((end_time - start_time) * 1000, 2)

        try:
            health_info["response_body"] = response.json()
        except:
            health_info["response_body"] = response.text

        if response.status_code == 200:
            health_info["status"] = "healthy"
        else:
            health_info["status"] = f"unhealthy (HTTP {response.status_code})"

    except requests.exceptions.ConnectionError as e:
        health_info["status"] = "connection_failed"
        health_info["error"] = str(e)
    except requests.exceptions.Timeout:
        health_info["status"] = "timeout"
        health_info["error"] = "Request timed out after 5 seconds"
    except Exception as e:
        health_info["status"] = "error"
        health_info["error"] = str(e)

    if detailed:
        print("\n" + "=" * 70)
        print("BACKEND HEALTH CHECK REPORT".center(70))
        print("=" * 70)
        print(f"Status:              {health_info['status'].upper()}")
        print(f"Endpoint:            {api_url}/health")
        print(f"Accessible:          {'✅ Yes' if health_info['endpoint_accessible'] else '❌ No'}")
        print(f"Status Code:         {health_info['status_code'] or 'N/A'}")
        print(f"Response Time:       {health_info['response_time_ms'] or 'N/A'} ms")
        print(f"Response Body:       {health_info['response_body'] or 'N/A'}")
        if health_info["error"]:
            print(f"Error Details:       {health_info['error']}")
        print("=" * 70 + "\n")

    return health_info


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

    # Kill any existing process on port 8000
    kill_process_on_port(8000)

    # Set environment variables for test database
    env = os.environ.copy()
    env["DATABASE_HOSTNAME"] = "localhost"
    env["DATABASE_PORT"] = "5432"
    env["DATABASE_NAME"] = "jam_test"
    env["DATABASE_USERNAME"] = "postgres"
    env["DATABASE_PASSWORD"] = "db_password"
    env["SQLALCHEMY_DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

    print(f"Using database URL: {SQLALCHEMY_DATABASE_URL}")
    print(f"Backend path: {backend_path}")

    # Add backend path to PYTHONPATH for proper imports
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{backend_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = backend_path

    # Start the backend server on a different port to avoid conflicts
    print("Starting backend subprocess...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=backend_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    print(f"Backend process started with PID: {process.pid}")

    # Wait for server to start
    api_url = "http://localhost:8000"
    print(f"Waiting for backend server to be ready at {api_url}...")

    backend_ready = False
    for attempt in range(30):  # 30 seconds max
        print(f"Attempt {attempt + 1}/30 - Checking backend server health...")

        # Check if process died
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Backend process died! Return code: {process.poll()}")
            print(f"STDOUT:\n{stdout}")
            print(f"STDERR:\n{stderr}")
            raise Exception(f"Backend server process terminated unexpectedly")

        # Check health endpoint
        health_info = check_backend_health(api_url, detailed=False)

        if health_info["status"] == "healthy":
            print("✅ Backend server is ready!")
            backend_ready = True
            break
        else:
            print(f"Backend status: {health_info['status']}")

        time.sleep(1)

    if not backend_ready:
        # Backend failed to start - show detailed health check
        print("❌ Backend server failed to start after 30 seconds")
        check_backend_health(api_url, detailed=True)

        kill_process_tree(process.pid)
        stdout, stderr = process.communicate(timeout=10)
        print(f"Backend STDOUT:\n{stdout}")
        print(f"Backend STDERR:\n{stderr}")
        raise Exception(f"Backend server failed to start")

    # Final health check with detailed output
    print("\n✅ Backend server startup completed successfully!")
    check_backend_health(api_url, detailed=True)

    yield api_url

    # Cleanup
    print("Cleaning up backend server...")
    kill_process_tree(process.pid)
    print("✅ Backend server cleanup completed.")
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
    yield frontend_url

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


@pytest.fixture
def api_base_url(test_backend_server) -> str:
    """Base URL for the API"""

    return test_backend_server


@pytest.fixture
def frontend_base_url(test_frontend_server) -> str:
    """Base URL for the frontend"""

    return test_frontend_server + "/jam"


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


def generate_entry_combinations(data_dict, required_keys: list[str], duplicate_keys: list[str]) -> list[dict]:
    """Generate all possible combinations of entries in the given dictionary,
    :param data_dict: The dictionary to search.
    :param required_keys: A list of required keys.
    :param duplicate_keys: A list of duplicate keys."""

    keys = list(data_dict.keys())
    i = 0
    result = []

    # Loop over all possible combination lengths
    for r in range(len(required_keys), len(keys) + 1):
        for combo in itertools.combinations(keys, r):
            # Only keep dicts that contain all keys in A
            if all(a in combo for a in required_keys):
                d = {}
                for k in combo:
                    if k in duplicate_keys:
                        d[k] = f"{data_dict[k]}_{i}"
                        i += 1
                    else:
                        d[k] = data_dict[k]
                if d:
                    result.append(d)
    return result


def check_backend_endpoint(
    api_url: str, endpoint: str, method: str = "GET", data: dict = None, headers: dict = None
) -> dict:
    """Check a specific backend endpoint and log the response

    :param api_url: Base URL of the API
    :param endpoint: Endpoint to check (e.g., '/login', '/users')
    :param method: HTTP method (GET, POST, etc.)
    :param data: Optional data to send with POST requests
    :param headers: Optional headers to send with request
    :return: Dictionary with response information
    """

    full_url = f"{api_url}{endpoint}"
    result = {
        "success": False,
        "status_code": None,
        "response_body": None,
        "error": None,
    }

    try:
        if method.upper() == "POST":
            response = requests.post(full_url, json=data, headers=headers, timeout=5)
        elif method.upper() == "PUT":
            response = requests.put(full_url, json=data, headers=headers, timeout=5)
        elif method.upper() == "DELETE":
            response = requests.delete(full_url, headers=headers, timeout=5)
        else:  # GET
            response = requests.get(full_url, headers=headers, timeout=5)

        result["status_code"] = response.status_code
        result["success"] = 200 <= response.status_code < 300

        try:
            result["response_body"] = response.json()
        except:
            result["response_body"] = response.text

        log_request_response(
            method=method,
            url=full_url,
            status_code=response.status_code,
            response_body=(
                json.dumps(result["response_body"])
                if isinstance(result["response_body"], dict)
                else result["response_body"]
            ),
        )

    except requests.exceptions.ConnectionError as e:
        result["error"] = f"Connection failed: {str(e)}"
        log_request_response(method=method, url=full_url, error=result["error"])
    except requests.exceptions.Timeout:
        result["error"] = "Request timed out after 5 seconds"
        log_request_response(method=method, url=full_url, error=result["error"])
    except Exception as e:
        result["error"] = str(e)
        log_request_response(method=method, url=full_url, error=result["error"])

    return result


def log_request_response(
    method: str,
    url: str,
    status_code: Optional[int] = None,
    response_body: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """Log HTTP request/response in a clean format for debugging"""

    print("\n" + "=" * 80)
    print(f"HTTP REQUEST/RESPONSE LOG".center(80))
    print("=" * 80)
    print(f"Method:          {method}")
    print(f"URL:             {url}")

    if status_code:
        status_icon = "✅" if 200 <= status_code < 300 else "❌"
        print(f"Status Code:     {status_icon} {status_code}")

    if response_body:
        try:
            # Try to pretty print JSON
            parsed = json.loads(response_body)
            print(f"Response Body:   {json.dumps(parsed, indent=2)}")
        except:
            print(f"Response Body:   {response_body}")

    if error:
        print(f"Error:           {error}")

    print("=" * 80 + "\n")


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

    def take_debug_screenshot(self, name: str = "debug") -> None:
        """Take a screenshot for debugging purposes"""

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"screenshots/{name}_{timestamp}.png"

        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)

        try:
            self.driver.save_screenshot(filename)
            print(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            print(f"Failed to save screenshot: {e}")

    def get_console_logs(self) -> list:
        """Get browser console logs for debugging"""

        try:
            logs = self.driver.get_log("browser")
            return logs
        except Exception as e:
            print(f"Could not get console logs: {e}")
            return []

    def print_console_logs(self) -> None:
        """Print all browser console logs in a readable format"""

        logs = self.get_console_logs()

        if not logs:
            print("No console logs found")
            return

        print("\n" + "=" * 80)
        print("BROWSER CONSOLE LOGS".center(80))
        print("=" * 80)

        for log in logs:
            level = log.get("level", "INFO")
            message = log.get("message", "")
            timestamp = log.get("timestamp", "")

            # Add emoji based on log level
            emoji = {"SEVERE": "🔴", "WARNING": "⚠️", "INFO": "ℹ️", "DEBUG": "🔍"}.get(level, "📝")

            print(f"{emoji} [{level}] {message}")

        print("=" * 80 + "\n")

    def print_page_state(self, label: str = "Page State") -> None:
        """Print comprehensive page state for debugging"""

        print("\n" + "=" * 80)
        print(f"{label.upper()}".center(80))
        print("=" * 80)
        print(f"Current URL:        {self.driver.current_url}")
        print(f"Page Title:         {self.driver.title}")
        print(f"Available IDs:      {len(self.get_all_element_ids())} elements")
        print("=" * 80)

        # Print console logs
        self.print_console_logs()

        # Take screenshot
        self.take_debug_screenshot(label.lower().replace(" ", "_"))

    def wait_for_network_idle(self, timeout: float = 5.0) -> None:
        """Wait for network requests to complete"""

        script = """
        return window.performance.getEntriesByType('resource')
            .filter(r => r.initiatorType === 'fetch' || r.initiatorType === 'xmlhttprequest')
            .length;
        """

        start_time = time.time()
        last_count = -1
        stable_count = 0

        while time.time() - start_time < timeout:
            current_count = self.driver.execute_script(script)

            if current_count == last_count:
                stable_count += 1
                if stable_count >= 3:  # Stable for 3 checks
                    print(f"✅ Network idle after {time.time() - start_time:.2f}s")
                    return
            else:
                stable_count = 0

            last_count = current_count
            time.sleep(0.5)

        print(f"⚠️  Network may still be active after {timeout}s")

    @pytest.fixture(autouse=True)
    def setup_method(
        self,
        frontend_base_url,
        api_base_url,
        request,
        test_users,
        authorised_clients,
        session,
    ) -> Generator[None, None, None]:
        """Set up the test environment before each test with test data"""
        user_data_dir = tempfile.mkdtemp()
        try:
            # Configure Chrome options to disable password prompts
            chrome_options = Options()
            prefs = {
                "profile.password_manager_leak_detection": False,
                "credentials_enable_service": False,
                "password_manager_enabled": False,
                "profile.password_manager_enabled": False,
            }
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_experimental_option("prefs", prefs)
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--ignore-certificate-errors")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # Enable verbose logging
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--v=1")

            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 10)

            # Frontend/Backend
            self.frontend_base_url = frontend_base_url
            self.backend_url = api_base_url

            # Client/User
            self.client = authorised_clients[self.user_index]
            self.user = test_users[self.user_index]
            self.db = session

            self.setup_function(request)

        except Exception:
            if hasattr(self, "driver"):
                try:
                    self.driver.quit()
                except:
                    pass
                if "user_data_dir" in locals() and os.path.exists(user_data_dir):
                    shutil.rmtree(user_data_dir, ignore_errors=True)
            raise

        yield  # This allows the test to run

        # Teardown
        try:
            if hasattr(self, "driver"):
                self.driver.quit()
        except Exception as e:
            print(f"Error during teardown: {e}")

    def setup_function(self, request) -> None:
        """Function to run before each test - can be overridden in subclasses"""
        pass

    def login(self) -> None:
        """Helper method to log in to the application"""

        login_url = f"{self.frontend_base_url}/login"
        self.driver.get(login_url)
        self.get_element("email").send_keys(self.user.email)
        self.get_element("password").send_keys(self.user.password)
        self.get_element("confirm-button").click()
        try:
            self.get_element("loading-spinner", timeout=2)
            self.wait_for_disappear("loading-spinner", timeout=2)
        except:
            pass
        self.wait_for_page("dashboard")
        self.driver.get(f"{self.frontend_base_url}/{self.page_url}")
        self.wait_for_table_load()

    # ------------------------------------------------ GET/WAIT ELEMENTS -----------------------------------------------

    def wait_for_page(self, page_url: str) -> None:
        """Wait for the dashboard to load"""

        print("Current URL!!!!!!!!!!!!!!!!", self.driver.current_url)
        print(self.driver.current_url.startswith(self.frontend_base_url))
        print(list(self.frontend_base_url))
        print(list(self.driver.current_url))
        print("Waiting for page to load:", f"{self.frontend_base_url}/{page_url}")
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
