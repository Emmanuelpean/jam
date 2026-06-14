"""Fixtures and helper functions for integration tests"""

import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from typing import Generator, Any

import psutil
import pytest
import requests

from app.config import settings

backend_path = os.path.abspath(os.path.join(str(__file__), "../../../backend"))
sys.path.insert(0, backend_path)
frontend_path = os.path.abspath(os.path.join(__file__, "../.."))


# Load the pytest fixtures
pytest_plugins = [
    "tests.fixtures.database",
    "tests.fixtures.clients",
    "tests.fixtures.users",
    "tests.fixtures.test_data",
    "tests.fixtures.job_scraping",
    "tests.fixtures.job_rating",
]


@pytest.fixture(scope="session", autouse=True)
def enable_test_mode() -> Generator[None, None, None]:
    """Enable test mode for the in-process TestClient (self.client).

    The uvicorn subprocess gets TEST_MODE=true via its env, but self.client runs the
    FastAPI app in this pytest process, where settings.test_mode comes from backend/.env
    (TEST_MODE=False locally). Without this, test-only endpoints return 403 locally even
    though they pass in CI (where TEST_MODE is set as a job env var)."""

    original = settings.test_mode
    settings.test_mode = True
    yield
    settings.test_mode = original


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


def kill_process_tree(parent_pid: int) -> None:
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
        port = 3100
    else:
        worker_num = int(worker_id.replace("gw", ""))
        port = 3100 + worker_num
    return f"http://localhost:{port}"


@pytest.fixture(scope="session")
def test_backend_server(database_url, worker_id, frontend_url, engine) -> Generator[str, None, None]:
    """Start a test backend server for integration tests"""
    print("=" * 60)
    print(f"STARTING BACKEND SERVER (Worker: {worker_id})")
    print("=" * 60)
    print_backend_pid()

    # Determine port based on worker_id
    if worker_id == "master":
        port = 8100
    else:
        # Extract worker number from worker_id (e.g., "gw0" -> 0)
        worker_num = int(worker_id.replace("gw", ""))
        port = 8100 + worker_num

    print(f"Using port: {port}")
    kill_process_on_port(port)

    env = os.environ.copy()
    env["SQLALCHEMY_DATABASE_URL"] = database_url
    env["TEST_MODE"] = "true"
    env["LOG_DIRECTORY"] = settings.log_directory
    env["FRONTEND_URL"] = frontend_url + "/jam"
    # Cloudflare Turnstile test keys — site key auto-solves; secret key always returns success
    env["TURNSTILE_SITE_KEY"] = "1x00000000000000000000AA"
    env["TURNSTILE_SECRET_KEY"] = "1x0000000000000000000000000000000AA"
    print(f"Using database URL: {database_url}")
    print(f"Backend path: {backend_path}")

    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{backend_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = backend_path

    # CREATE LOG FILES FOR BACKEND OUTPUT
    backend_log_file = settings.log_directory + f"/backend_server_{worker_id}.log"
    backend_error_file = settings.log_directory + f"/backend_errors_{worker_id}.log"

    with (
        open(backend_log_file, "w") as log_out,
        open(backend_error_file, "w") as log_err,
    ):
        print(f"Backend logs will be saved to: {backend_log_file}")

        # Start backend with worker-specific port
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                str(port),
            ],
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
                raise Exception("Backend server process terminated unexpectedly")

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
            raise Exception("Backend server failed to start")

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

    print(f"Frontend path: {frontend_path}")

    # Set environment variables for frontend
    env = os.environ.copy()
    env["VITE_API_BASE_URL"] = test_backend_server  # Use worker-specific backend
    env["VITE_API_SERVICE_URL"] = test_backend_server  # Scheduler routes also served by test backend
    print("Environment variables:")
    print(f"  VITE_API_BASE_URL: {env['VITE_API_BASE_URL']}")
    print(f"  VITE_API_SERVICE_URL: {env['VITE_API_SERVICE_URL']}")

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
        f'"{npm_cmd}" start -- --port {port}',
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
    print("This will take a few seconds for Vite to start...")

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
            raise Exception("Frontend server process terminated unexpectedly")

        recent_lines = []
        while not output_queue.empty():
            line = output_queue.get()
            recent_lines.append(line)

            if "ready in" in line.lower() or ("local:" in line.lower() and "localhost" in line.lower()):
                compiled = True
                print(f"\u2705 Frontend ready: {line}")
            elif "error" in line.lower() and ("failed" in line.lower() or "cannot" in line.lower()):
                print("❌ Frontend compilation failed!")
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


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call) -> Generator[None, Any, None]:
    """Attach test failure information to the request node."""
    _ = call
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
