"""GIF Generator Script for Dashboard Customisation Demo"""

import argparse
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

from demo_creator import DemoBuilder

COLS = 12


class DashboardBuilder(DemoBuilder):
    """Records the dashboard customisation workflow and generates a GIF"""

    def record(self, email: str, password: str) -> None:
        """Record the dashboard flow: remove a widget, add upcoming interviews, resize two widgets, save"""

        print("Recording dashboard flow...")

        self.login_silently(email, password)

        print("  - Navigating to dashboard...")
        self.driver.get(f"{self.frontend_url}/dashboard")
        time.sleep(3)
        self.inject_highlighting()

        print("  - Capturing dashboard...")
        self.capture_frames_for_duration(2.0)

        # Enter edit mode
        print("  - Entering edit mode...")
        self.move_to_element("dashboard-edit-btn", 500)
        self.click_element("dashboard-edit-btn")
        time.sleep(0.5)
        self.capture_frames_for_duration(1.0)

        # Remove the Recent Activity widget
        print("  - Removing recent activity widget...")
        self.move_to_element("widget-remove-btn-w-default-recent-activity", 400)
        self.click_element("widget-remove-btn-w-default-recent-activity")
        self.wait.until(ec.presence_of_element_located((By.ID, "delete-alert-modal")))
        self.capture_frames_for_duration(0.8)
        self.move_to_element("delete-alert-modal-confirm-button", 400)
        self.click_element("delete-alert-modal-confirm-button")
        time.sleep(0.5)
        self.capture_frames_for_duration(1.0)

        # Add Upcoming Interviews widget
        print("  - Opening widget picker...")
        self.move_to_element("dashboard-add-widget-btn", 400)
        self.click_element("dashboard-add-widget-btn")
        time.sleep(0.4)
        self.capture_frames_for_duration(0.8)

        print("  - Selecting timeline type...")
        self.move_to_element("widget-picker-type-timeline", 400)
        self.click_element("widget-picker-type-timeline")
        time.sleep(0.3)
        self.capture_frames_for_duration(0.8)

        print("  - Selecting upcoming interviews variant...")
        self.move_to_element("widget-picker-variant-upcoming_interviews", 400)
        self.click_element("widget-picker-variant-upcoming_interviews")
        time.sleep(0.5)
        self.capture_frames_for_duration(1.0)

        col_width = (
            self.driver.execute_script("return document.querySelector('.dashboard-main').getBoundingClientRect().width")
            / COLS
        )

        # Scroll down so the y=8 widget row is centred in the viewport
        print("  - Scrolling to widget row...")
        self.driver.execute_script("window.scrollBy({top: 220, behavior: 'smooth'})")
        time.sleep(0.5)
        self.capture_frames_for_duration(0.8)

        # Narrow the follow-up table via its SW handle (left edge moves right, creates space on the left)
        print("  - Resizing follow-up table narrower...")
        self._drag_handle("table-card-follow_up", "react-resizable-handle-sw", dx_cols=+2, col_width=col_width)
        self.capture_frames_for_duration(0.8)

        # Widen the new upcoming-interviews widget via its SE handle (right edge grows into freed space)
        print("  - Resizing upcoming interviews wider...")
        self._drag_handle_topmost(
            "activity-card-upcoming_interviews", "react-resizable-handle-se", dx_cols=+2, col_width=col_width
        )
        self.capture_frames_for_duration(0.8)

        # Save
        print("  - Saving layout...")
        self.move_to_element("dashboard-save-btn", 400)
        self.click_element("dashboard-save-btn")
        time.sleep(1)
        self.capture_frames_for_duration(2.0)

        print(f"Captured {len(self.frames)} frames")

    def _drag_handle(self, content_id: str, handle_class: str, dx_cols: int, col_width: float) -> None:
        """Drag a resize handle of the grid item containing content_id by dx_cols columns."""

        grid_item = self.driver.execute_script(
            "const w = document.getElementById(arguments[0]); return w ? w.closest('.dashboard-grid-item') : null;",
            content_id,
        )
        self._do_drag(grid_item, handle_class, dx_cols, col_width)

    def _drag_handle_topmost(self, content_id: str, handle_class: str, dx_cols: int, col_width: float) -> None:
        """Like _drag_handle but picks the grid item highest on the page when duplicates exist."""

        grid_item = self.driver.execute_script(
            """
            const items = Array.from(document.querySelectorAll('.dashboard-grid-item'))
                .filter(el => el.querySelector('[id="' + arguments[0] + '"]'));
            items.sort((a, b) =>
                (a.getBoundingClientRect().top + window.scrollY) -
                (b.getBoundingClientRect().top + window.scrollY)
            );
            return items[0] || null;
            """,
            content_id,
        )
        self._do_drag(grid_item, handle_class, dx_cols, col_width)

    def _do_drag(self, grid_item, handle_class: str, dx_cols: int, col_width: float) -> None:
        """Perform a horizontal drag on a resize handle, capturing frames step by step."""

        handle = grid_item.find_element(By.CSS_SELECTOR, f".{handle_class}")
        handle_rect = self.driver.execute_script(
            "const r = arguments[0].getBoundingClientRect(); return {x: r.left + r.width/2, y: r.top + r.height/2};",
            handle,
        )

        self.driver.execute_script(f"window.moveCursorTo({handle_rect['x']}, {handle_rect['y']}, 400);")
        self.capture_frames_for_duration(0.5)

        ActionChains(self.driver).move_to_element(handle).click_and_hold().perform()
        self.driver.execute_script(f"window.simulateClick({handle_rect['x']}, {handle_rect['y']});")

        total_dx = int(dx_cols * col_width)
        steps = 10
        step_dx = total_dx // steps
        cur_x = handle_rect["x"]

        for _ in range(steps):
            ActionChains(self.driver).move_by_offset(step_dx, 0).perform()
            cur_x += step_dx
            self.driver.execute_script(
                f"window.demoCursorX={cur_x};"
                f"document.getElementById('demo-cursor').style.left='{cur_x}px';"
                f"document.getElementById('demo-cursor-ring').style.left='{cur_x}px';"
            )
            self.capture_frame()
            time.sleep(0.04)

        ActionChains(self.driver).release().perform()
        time.sleep(0.3)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-headless", action="store_true", help="Show browser window (default: headless)")
    args = parser.parse_args()

    recorder = DashboardBuilder(output_name="dashboard_customisation.gif", headless=not args.no_headless)
    recorder.run()
