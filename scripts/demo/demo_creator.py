"""
Shared Demo Recorder Infrastructure

Base module for recording browser interactions and generating GIF demos.
Provides DemoRecorder with hooks for subclasses to customize database setup,
browser preferences, and recording flow.
"""

import io
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import psutil
import requests
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from tests.utils.test_data import USER_DATA

# Backend/frontend paths
backend_path = Path(__file__).parent.parent.parent / "backend"
frontend_path = Path(__file__).parent.parent.parent / "frontend"

sys.path.insert(0, str(backend_path))

from app.database import create_db_url
from app.config import settings
from tests.utils.seed_database import reset_database, create_database_data
from tests.utils.create_data.core import create_users

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings.test_mode = True

# CSS for cursor and click highlighting
HIGHLIGHT_CSS = """
/* Custom cursor that's always visible */
* {
    cursor: none !important;
}

#demo-cursor {
    position: fixed;
    width: 20px;
    height: 20px;
    background: radial-gradient(circle, rgba(255,100,100,1) 0%, rgba(255,100,100,0.8) 40%, rgba(255,100,100,0) 70%);
    border-radius: 50%;
    pointer-events: none;
    z-index: 999999;
    transform: translate(-50%, -50%);
    transition: transform 0.05s ease-out;
}

#demo-cursor.clicking {
    transform: translate(-50%, -50%) scale(1.5);
    background: radial-gradient(circle, rgba(255,50,50,1) 0%, rgba(255,50,50,0.9) 50%, rgba(255,50,50,0) 80%);
}

#demo-cursor-ring {
    position: fixed;
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255,100,100,0.6);
    border-radius: 50%;
    pointer-events: none;
    z-index: 999998;
    transform: translate(-50%, -50%);
    transition: all 0.1s ease-out;
}

#demo-cursor-ring.clicking {
    width: 60px;
    height: 60px;
    border-color: rgba(255,50,50,0.8);
    border-width: 4px;
}

/* Click ripple effect */
.click-ripple {
    position: fixed;
    width: 10px;
    height: 10px;
    background: transparent;
    border: 3px solid rgba(255,100,100,0.8);
    border-radius: 50%;
    pointer-events: none;
    z-index: 999997;
    transform: translate(-50%, -50%);
    animation: ripple 0.6s ease-out forwards;
}

@keyframes ripple {
    0% {
        width: 10px;
        height: 10px;
        opacity: 1;
        border-width: 3px;
    }
    100% {
        width: 80px;
        height: 80px;
        opacity: 0;
        border-width: 1px;
    }
}

/* Typing indicator */
.typing-indicator {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    display: flex;
    gap: 3px;
}

.typing-indicator span {
    width: 6px;
    height: 6px;
    background: #666;
    border-radius: 50%;
    animation: typing 1s infinite;
}

.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.2); }
}
"""

# JavaScript for cursor tracking and click effects
HIGHLIGHT_JS = """
(function() {
    // Create cursor elements
    const cursor = document.createElement('div');
    cursor.id = 'demo-cursor';
    document.body.appendChild(cursor);

    const ring = document.createElement('div');
    ring.id = 'demo-cursor-ring';
    document.body.appendChild(ring);

    // Store cursor position for external access
    window.demoCursorX = 0;
    window.demoCursorY = 0;

    // Update cursor position
    document.addEventListener('mousemove', (e) => {
        window.demoCursorX = e.clientX;
        window.demoCursorY = e.clientY;
        cursor.style.left = e.clientX + 'px';
        cursor.style.top = e.clientY + 'px';
        ring.style.left = e.clientX + 'px';
        ring.style.top = e.clientY + 'px';
    });

    // Click effect
    document.addEventListener('mousedown', (e) => {
        cursor.classList.add('clicking');
        ring.classList.add('clicking');

        // Create ripple
        const ripple = document.createElement('div');
        ripple.className = 'click-ripple';
        ripple.style.left = e.clientX + 'px';
        ripple.style.top = e.clientY + 'px';
        document.body.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    });

    document.addEventListener('mouseup', () => {
        cursor.classList.remove('clicking');
        ring.classList.remove('clicking');
    });

    // Function to programmatically move cursor with animation
    window.moveCursorTo = function(x, y, duration = 500) {
        return new Promise((resolve) => {
            const startX = window.demoCursorX || 0;
            const startY = window.demoCursorY || 0;
            const startTime = Date.now();

            function animate() {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Ease-out cubic
                const eased = 1 - Math.pow(1 - progress, 3);

                const currentX = startX + (x - startX) * eased;
                const currentY = startY + (y - startY) * eased;

                window.demoCursorX = currentX;
                window.demoCursorY = currentY;
                cursor.style.left = currentX + 'px';
                cursor.style.top = currentY + 'px';
                ring.style.left = currentX + 'px';
                ring.style.top = currentY + 'px';

                if (progress < 1) {
                    requestAnimationFrame(animate);
                } else {
                    resolve();
                }
            }
            animate();
        });
    };

    // Function to simulate click effect at position
    window.simulateClick = function(x, y) {
        cursor.classList.add('clicking');
        ring.classList.add('clicking');

        const ripple = document.createElement('div');
        ripple.className = 'click-ripple';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        document.body.appendChild(ripple);

        setTimeout(() => {
            cursor.classList.remove('clicking');
            ring.classList.remove('clicking');
            ripple.remove();
        }, 300);
    };

    console.log('Demo cursor initialized');
})();
"""


def kill_process_on_port(port: int) -> bool:
    """Kill any process using the specified port"""
    try:
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                connections = proc.net_connections()
                for conn in connections:
                    if hasattr(conn, "laddr") and conn.laddr.port == port:
                        print(f"Killing process on port {port} (PID: {proc.info['pid']})")
                        proc.kill()
                        proc.wait(timeout=5)
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        print(f"Error checking port {port}: {e}")
    return False


class DemoBuilder:
    """Records browser interactions and generates GIF demos."""

    def __init__(
        self,
        output_dir: str = "../../frontend/src/assets/",
        output_name: str = "demo.gif",
        fps: int = 30,
        headless: bool = True,
        width: int = 1500,
        height: int = 850,
        scale_factor: int = 1,
        speed: float = 0.25,
        dark_mode: bool = False,
    ) -> None:
        """Object constructor
        :param output_name: Name for the output GIF file.
        :param fps: Frames per second for the GIF.
        :param headless: Whether to run the browser in headless mode.
        :param width: Width of the browser window.
        :param height: Height of the browser window.
        :param scale_factor: Scale factor for the browser window.
        :param speed: Playback speed multiplier (e.g. 0.5 = half speed, 2.0 = double speed).
        :param dark_mode: Whether to use dark mode for the browser."""

        self.gif_output_path = Path(output_dir + "/demo_gifs/" + output_name)
        self.screenshot_output_path = Path(output_dir + "/screenshots/")
        self.fps = fps
        self.speed = speed
        self.headless = headless
        self.width = width
        self.height = height
        self.scale_factor = scale_factor
        self.dark_mode = dark_mode

        # GIF parameters
        self.frames: list[Image.Image] = []
        self.driver = None
        self.wait = None

        # App
        self.backend_process = None
        self.frontend_process = None
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000/jam"

    def create_demo_data(self, db, users) -> None:
        """Hook for subclasses to create additional demo data.
        Called by setup_database() after users and settings are created.
        Default implementation loads all the data."""

        create_database_data(db, users=users)

    def setup_database(self) -> tuple[str, str]:
        """Set up test database with fixtures"""

        print("Setting up test database...")

        if sys.platform == "win32":
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

        test_db_url = create_db_url("jam_test")

        test_engine = create_engine(test_db_url)
        TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        reset_database(test_engine, ask_confirmation=False)

        db = TestSessionLocal()
        try:
            data = USER_DATA.copy()
            users = create_users(db, data, rounds=4)
            self.create_demo_data(db, users)

            if self.dark_mode:
                for user in users:
                    user.preferences.dark_mode = "dark"
                    user.preferences.theme = "blueberry"
                    user.preferences.extension_banner_dismissed = True
                db.commit()

            return users[0].email, users[0].plain_password
        finally:
            db.close()
            test_engine.dispose()

    def start_backend(self):
        """Start the backend server"""

        print("Starting backend server...")
        kill_process_on_port(8000)

        test_db_url = create_db_url("jam_test")

        env = os.environ.copy()
        env["TEST_MODE"] = "true"
        env["SQLALCHEMY_DATABASE_URL"] = test_db_url

        self.backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(backend_path),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        for _ in range(30):
            try:
                response = requests.get(f"{self.backend_url}/health", timeout=2)
                if response.status_code == 200:
                    print("Backend server ready")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        raise Exception("Backend failed to start")

    def start_frontend(self) -> None:
        """Start the frontend server"""

        print("Starting frontend server...")
        kill_process_on_port(3000)

        # noinspection PyDeprecation
        npm_cmd = shutil.which("npm") or shutil.which("npm.cmd")

        env = os.environ.copy()
        env["REACT_APP_API_BASE_URL"] = self.backend_url
        env["PORT"] = "3000"
        env["BROWSER"] = "none"

        self.frontend_process = subprocess.Popen(
            f'"{npm_cmd}" start',
            cwd=str(frontend_path),
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )

        print("Waiting for frontend to compile (this may take 30-60 seconds)...")
        for attempt in range(90):
            try:
                response = requests.get("http://localhost:3000", timeout=3)
                if response.status_code == 200:
                    print("Frontend server ready")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        raise Exception("Frontend failed to start")

    def setup_browser(self) -> None:
        """Set up Chrome browser with custom options"""

        print("Setting up browser...")
        chrome_preferences = {
            "profile.password_manager_leak_detection": False,
            "credentials_enable_service": False,
            "password_manager_enabled": False,
        }
        chrome_options = Options()
        chrome_options.add_experimental_option("prefs", chrome_preferences)
        chrome_options.add_argument(f"--window-size={self.width},{self.height}")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument(f"--force-device-scale-factor={self.scale_factor}")
        chrome_options.add_argument("--disable-dev-shm-usage")

        if self.headless:
            chrome_options.add_argument("--headless=new")
            print("  Running in headless mode")
        else:
            print("  Running in visible mode (for debugging)")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get(self.frontend_url)
        time.sleep(2)

        self.inject_highlighting()

    def inject_highlighting(self) -> None:
        """Inject CSS and JS for cursor highlighting"""

        self.driver.execute_script(
            f"""
            const style = document.createElement('style');
            style.textContent = `{HIGHLIGHT_CSS}`;
            document.head.appendChild(style);
        """
        )

        self.driver.execute_script(HIGHLIGHT_JS)
        time.sleep(0.5)

    def capture_frame(self) -> None:
        """Capture current browser state as a frame"""

        try:
            screenshot = self.driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(screenshot))
            self.frames.append(image)
        except Exception as e:
            print(f"  Warning: Failed to capture frame: {e}")

    def capture_frames_for_duration(self, duration_seconds: float, interval: float = 0.1) -> None:
        """Capture frames for a duration
        :param duration_seconds: Duration in seconds.
        :param interval: Interval between frames in seconds."""

        end_time = time.time() + duration_seconds
        while time.time() < end_time:
            self.capture_frame()
            time.sleep(interval)

    def move_to_element(self, element_id: str, duration_ms: int = 500) -> None:
        """Move cursor to element with animation
        :param element_id: ID of the element.
        :param duration_ms: Duration of the animation in milliseconds."""

        element = self.wait.until(ec.presence_of_element_located((By.ID, element_id)))
        rect = self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
            """,
            element,
        )

        self.driver.execute_script(f"window.moveCursorTo({rect['x']}, {rect['y']}, {duration_ms});")

        self.capture_frames_for_duration(duration_ms / 1000 + 0.1)

    def click_element(self, element_id: str) -> None:
        """Click element with visual effect
        :param element_id: ID of the element."""

        element = self.wait.until(ec.element_to_be_clickable((By.ID, element_id)))
        rect = self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
        """,
            element,
        )

        self.driver.execute_script(f"window.simulateClick({rect['x']}, {rect['y']});")
        self.capture_frames_for_duration(0.3)

        element.click()
        time.sleep(0.2)
        self.capture_frames_for_duration(0.3)

    def type_text(self, element_id: str, text: str, delay: float = 0.08) -> None:
        """Type text with visual typing effect
        :param element_id: ID of the element.
        :param text: Text to type.
        :param delay: Delay between key presses in seconds."""

        element = self.wait.until(ec.presence_of_element_located((By.ID, element_id)))

        for char in text:
            element.send_keys(char)
            self.capture_frame()
            time.sleep(delay)

        self.capture_frames_for_duration(0.3)

    def login_silently(self, email: str, password: str) -> None:
        """Login without capturing frames
        :param email: Email address.
        :param password: Password."""

        print("Logging in silently...")
        self.driver.get(f"{self.frontend_url}/login")
        time.sleep(1)

        email_field = self.wait.until(ec.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(email)

        password_field = self.wait.until(ec.presence_of_element_located((By.ID, "password")))
        password_field.send_keys(password)

        confirm_button = self.wait.until(ec.element_to_be_clickable((By.ID, "confirm-button")))
        confirm_button.click()

        time.sleep(3)
        print("  Login complete")

    def right_click_element(self, element_id: str) -> None:
        """Right-click an element to open context menu with visual effect
        :param element_id: ID of the element."""

        element = self.wait.until(ec.presence_of_element_located((By.ID, element_id)))
        rect = self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            return {x: rect.left + rect.width/2, y: rect.top + rect.height/2};
        """,
            element,
        )

        self.driver.execute_script(f"window.simulateClick({rect['x']}, {rect['y']});")
        self.capture_frames_for_duration(0.3)

        actions = ActionChains(self.driver)
        actions.context_click(element).perform()
        time.sleep(0.3)
        self.capture_frames_for_duration(0.3)

    def generate_gif(self) -> None:
        """Generate GIF from captured frames"""

        print(f"Generating GIF with {len(self.frames)} frames...")

        if not self.frames:
            print("No frames captured!")
            return

        processed_frames = []
        for frame in self.frames:
            if frame.mode == "RGBA":
                frame = frame.convert("RGB")
            processed_frames.append(frame)

        duration = int((1000 / self.fps) / self.speed)  # milliseconds per frame

        processed_frames[0].save(
            self.gif_output_path,
            save_all=True,
            append_images=processed_frames[1:],
            duration=duration,
            loop=0,
        )

        print(f"GIF saved to: {self.gif_output_path}")
        print(f"  - Frames: {len(self.frames)}")
        print(f"  - FPS: {self.fps}")
        print(f"  - Duration: {len(self.frames) / self.fps:.1f}s")

    def cleanup(self) -> None:
        """Clean up resources"""

        print("Cleaning up...")

        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass

        if self.backend_process:
            try:
                parent = psutil.Process(self.backend_process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except (psutil.NoSuchProcess, Exception):
                pass

        if self.frontend_process:
            try:
                parent = psutil.Process(self.frontend_process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except (psutil.NoSuchProcess, Exception):
                pass

        kill_process_on_port(8000)
        kill_process_on_port(3000)

    def record(self, email: str, password: str) -> None:
        """Record the demo flow. Must be implemented by subclasses."""

        raise NotImplementedError("Subclasses must implement record()")

    def run(self) -> None:
        """Run the complete recording process"""

        try:
            email, password = self.setup_database()

            self.start_backend()
            self.start_frontend()

            self.setup_browser()
            self.record(email, password)

            self.generate_gif()

        finally:
            self.cleanup()

    def screenshot(self, pages: list[str]) -> None:
        """Take screenshots of each page.
        :param pages: List of page names to screenshot."""

        try:
            email, password = self.setup_database()

            self.start_backend()
            self.start_frontend()

            self.setup_browser()

            self.login_silently(email, password)

            self.screenshot_output_path.mkdir(parents=True, exist_ok=True)

            for page in pages:
                url = f"{self.frontend_url}/{page}"
                print(f"  Screenshotting: {page}...")

                self.driver.get(url)
                WebDriverWait(self.driver, 60).until(ec.invisibility_of_element_located((By.ID, "loading-spinner")))
                time.sleep(1)

                screenshot_path = self.screenshot_output_path / f"{page}.png"
                self.driver.save_screenshot(str(screenshot_path))
                print(f"    Saved: {screenshot_path}")

            print(f"Done. {len(pages)} screenshots saved to {self.screenshot_output_path}/")

        finally:
            self.cleanup()
