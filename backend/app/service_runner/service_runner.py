"""Module to run a generic service periodically in a separate thread."""

import threading
import time
from typing import Callable

from app.utilities.logger import AppLogger, get_last_log_line


class ServiceRunner:
    """Class to run a generic service periodically in a separate thread"""

    def __init__(
        self,
        service_name: str,
        service_function: Callable,
        service_kwargs: dict | None = None,
        period_hours: int | float = 3,
    ) -> None:
        """Initialise the service runner instance.
        :param service_name: name of the service
        :param service_kwargs: keyword arguments for service function
        :param service_function: function to run periodically
        :param period_hours: max hours between runs"""

        self.service_name = service_name
        self.service_kwargs = {} if not service_kwargs else service_kwargs
        self.service_function = service_function
        self.period_hours = period_hours
        self.service_runner_name = self.service_name + "_runner"
        self.service_runner_thread = None
        self.stop_event = threading.Event()
        self.service_runner_thread_status = "stopped"
        self.service_running = False
        self.sleep_until = None
        self.sleep_start = None
        self.logger = AppLogger.create_service_logger(self.service_runner_name, "INFO")
        self.logger.info(self.service_runner_name + " initialised")

    def start_runner(self, period_hours: float = 3.0, **kwargs) -> None:
        """Start the service runner
        :param period_hours: Maximum hours between each service run
        :param kwargs: keyword arguments passed to the service_function"""

        if self.service_runner_thread_status in ("started", "starting", "stopping"):
            self.logger.warning(f"Cannot start service runner - current status: {self.service_runner_thread_status}")
            return

        self.logger.info(f"Starting service runner (period: {period_hours}h)")
        self.service_runner_thread_status = "starting"

        # Store parameters
        self.period_hours = period_hours
        for kwarg in kwargs:
            self.service_kwargs[kwarg] = kwargs[kwarg]

        # Clear the stop event
        self.stop_event.clear()

        # Start the service in a separate thread
        self.service_runner_thread = threading.Thread(
            target=self._run_service,
            args=(period_hours,),
        )
        self.service_runner_thread.daemon = True
        self.service_runner_thread.start()

    def stop_runner(self) -> None:
        """Stop the scraping service"""

        if self.service_runner_thread_status in ("stopped", "starting", "stopping"):
            self.logger.warning(f"Cannot stop service - current status: {self.service_runner_thread_status}")
            return

        self.logger.info("Stopping service")
        self.service_runner_thread_status = "stopping"
        self.stop_event.set()

    def _run_service(self, period_hours: float) -> None:
        """Internal method that runs the service
        :param period_hours: Hours between each scraping run"""

        try:
            self.service_runner_thread_status = "started"
            self.logger.info("Service runner thread started successfully")

            while not self.stop_event.is_set():
                try:
                    # Run the scraping
                    self.logger.info(f"Starting service ({self.service_kwargs})")
                    self.service_running = True
                    result = self.service_function(**self.service_kwargs)
                    self.service_running = False

                    self.logger.info(f"Service completed - duration: {result.run_duration:.2f}s")

                    duration = result.run_duration
                    sleep_time = max([0, period_hours * 3600 - duration])

                    # Track sleep timing
                    self.sleep_start = time.time()
                    self.sleep_until = self.sleep_start + sleep_time

                    self.logger.info(f"Sleeping for {sleep_time:.2f}s until next run")

                    if self.stop_event.wait(timeout=sleep_time):
                        self.logger.info("Stop event received during sleep")
                        break

                    # Clear sleep tracking after waking
                    self.sleep_start = None
                    self.sleep_until = None

                except Exception as e:
                    self.logger.exception(f"Error during service runner: {e}")
                    self.service_running = False

                    self.sleep_start = time.time()
                    self.sleep_until = self.sleep_start + 300

                    self.logger.info("Waiting 5 minutes before retry after error")

                    if self.stop_event.wait(timeout=300):  # 5 minutes
                        self.logger.info("Stop event received during error recovery")
                        break

                    self.sleep_start = None
                    self.sleep_until = None
        finally:
            self.logger.info("Service runner ended")
            self.service_runner_thread_status = "stopped"
            self.sleep_start = None
            self.sleep_until = None

    def status(self) -> dict:
        """Get the current status of the service"""

        return {
            "service_runner_status": self.service_runner_thread_status,
            "service_running": self.service_running,
            "service_kwargs": self.service_kwargs,
            "period_hours": self.period_hours,
            "sleep_until": self.sleep_until,
            "last_log": get_last_log_line(self.service_name),
        }
