import os
import queue
import shutil
import subprocess
import sys
import threading
import time
from typing import Generator

import pytest
import psutil
import requests

backend_path = os.path.join(os.path.dirname(__file__), "..", "..", "backend")
sys.path.insert(0, backend_path)

from tests.conftest import session, models, test_users, SQLALCHEMY_DATABASE_URL


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
    )

    print(f"Backend process started with PID: {process.pid}")

    # Wait for server to start
    api_url = "http://localhost:8000"
    print(f"Waiting for backend server to be ready at {api_url}...")

    for attempt in range(30):  # 30 seconds max
        print(f"Attempt {attempt + 1}/30 - Checking backend server health...")

        # Check if process died
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print(f"❌ Backend process died! Return code: {process.poll()}")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
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
        # Backend failed to start
        print("❌ Backend server failed to start after 30 seconds")
        kill_process_tree(process.pid)
        stdout, stderr = process.communicate(timeout=10)
        print(f"Backend STDOUT: {stdout}")
        print(f"Backend STDERR: {stderr}")
        raise Exception(f"Backend server failed to start. STDERR: {stderr}")

    print("✅ Backend server startup completed successfully!")
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
    return test_frontend_server


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


def contiguous_subdicts_with_required(dictionary: dict, required_keys: list) -> list[dict]:
    """Return a list of all contiguous sub-dictionaries in the given dictionary,
    :param dictionary: The dictionary to search.
    :param required_keys: A list of required keys."""

    keys = list(dictionary.keys())
    n = len(keys)
    seen = set()
    results = []
    for size in range(1, n + 1):
        for start in range(n):
            subkeys = [keys[(start + i) % n] for i in range(size)]
            # Only filter if required_keys is not empty
            if not required_keys or all(k in subkeys for k in required_keys):
                subdict = {k: dictionary[k] for k in subkeys}
                # Use sorted items as a hashable representation:
                key_tuple = tuple(sorted(subdict.items()))
                if key_tuple not in seen:
                    seen.add(key_tuple)
                    results.append(subdict)
    return results
