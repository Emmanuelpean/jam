"""Unit tests for app/service_runner/service_runner.py."""

import threading
from unittest.mock import MagicMock, patch

import pytest

from app.service_runner.service_runner import ServiceRunner


# -------------------------------------------------- FIXTURES --------------------------------------------------


def make_service_result(run_duration: float = 1.0) -> MagicMock:
    """Return a mock service result with a run_duration attribute."""
    result = MagicMock()
    result.run_duration = run_duration
    return result


@pytest.fixture
def mock_service_fn():
    """A service function that returns a result with run_duration=0.1."""
    fn = MagicMock(return_value=make_service_result(0.1))
    return fn


@pytest.fixture
def runner(mock_service_fn):
    """A ServiceRunner with all logging suppressed."""
    with patch("app.service_runner.service_runner.AppLogger") as mock_logger_cls:
        mock_logger_cls.create_service_logger.return_value = MagicMock()
        sr = ServiceRunner(
            service_name="test_svc",
            service_function=mock_service_fn,
            service_kwargs={"key": "val"},
            period_hours=1,
        )
    return sr


# ------------------------------------------------- __INIT__ ---------------------------------------------------


class TestInit:

    def test_initial_status_is_stopped(self, runner) -> None:
        assert runner.service_runner_thread_status == "stopped"

    def test_service_not_running(self, runner) -> None:
        assert runner.service_running is False

    def test_sleep_fields_are_none(self, runner) -> None:
        assert runner.sleep_until is None
        assert runner.sleep_start is None

    def test_attributes_set_from_params(self, mock_service_fn) -> None:
        with patch("app.service_runner.service_runner.AppLogger"):
            sr = ServiceRunner("svc", mock_service_fn, {"a": 1}, period_hours=5)
        assert sr.service_name == "svc"
        assert sr.service_function is mock_service_fn
        assert sr.service_kwargs == {"a": 1}
        assert sr.period_hours == 5

    def test_empty_kwargs_defaults_to_empty_dict(self, mock_service_fn) -> None:
        with patch("app.service_runner.service_runner.AppLogger"):
            sr = ServiceRunner("svc", mock_service_fn)
        assert sr.service_kwargs == {}

    def test_stop_event_is_threading_event(self, runner) -> None:
        assert isinstance(runner.stop_event, threading.Event)

    def test_runner_name_is_service_name_plus_runner(self, runner) -> None:
        assert runner.service_runner_name == "test_svc_runner"


# ----------------------------------------------- START RUNNER ------------------------------------------------


class TestStartRunner:

    def test_start_creates_daemon_thread(self, runner) -> None:
        with patch.object(runner, "_run_service"):
            runner.start_runner(period_hours=2)
        assert runner.service_runner_thread is not None
        assert runner.service_runner_thread.daemon is True

    def test_start_sets_period_hours(self, runner) -> None:
        with patch.object(threading, "Thread") as mock_thread_cls:
            mock_thread_cls.return_value = MagicMock()
            runner.start_runner(period_hours=4)
        assert runner.period_hours == 4

    def test_start_merges_extra_kwargs(self, runner) -> None:
        with patch.object(threading, "Thread") as mock_thread_cls:
            mock_thread_cls.return_value = MagicMock()
            runner.start_runner(period_hours=1, extra="abc")
        assert runner.service_kwargs["extra"] == "abc"

    def test_start_clears_stop_event(self, runner) -> None:
        runner.stop_event.set()
        with patch.object(threading, "Thread") as mock_thread_cls:
            mock_thread_cls.return_value = MagicMock()
            runner.start_runner(period_hours=1)
        assert not runner.stop_event.is_set()

    @pytest.mark.parametrize("blocked_status", ["started", "starting", "stopping"])
    def test_start_blocked_when_already_active(self, runner, blocked_status) -> None:
        runner.service_runner_thread_status = blocked_status
        with patch.object(threading, "Thread") as mock_thread_cls:
            runner.start_runner(period_hours=1)
        mock_thread_cls.assert_not_called()
        assert runner.service_runner_thread_status == blocked_status

    def test_start_sets_status_to_starting(self, runner) -> None:
        captured = {}

        def fake_thread_init(**_kwargs):
            """Fake thread init that captures the status."""
            captured["status_at_init"] = runner.service_runner_thread_status
            t = MagicMock()
            t.daemon = False
            return t

        with patch.object(threading, "Thread", side_effect=fake_thread_init):
            runner.start_runner(period_hours=1)

        assert captured["status_at_init"] == "starting"


# ------------------------------------------------ STOP RUNNER ------------------------------------------------


class TestStopRunner:

    def test_stop_sets_stop_event(self, runner) -> None:
        runner.service_runner_thread_status = "started"
        runner.stop_runner()
        assert runner.stop_event.is_set()

    def test_stop_sets_status_to_stopping(self, runner) -> None:
        runner.service_runner_thread_status = "started"
        runner.stop_runner()
        assert runner.service_runner_thread_status == "stopping"

    @pytest.mark.parametrize("blocked_status", ["stopped", "starting", "stopping"])
    def test_stop_blocked_when_not_running(self, runner, blocked_status) -> None:
        runner.service_runner_thread_status = blocked_status
        runner.stop_runner()
        assert not runner.stop_event.is_set()
        assert runner.service_runner_thread_status == blocked_status


# ---------------------------------------------- _RUN_SERVICE -------------------------------------------------


class TestRunService:

    def test_sets_status_to_started_then_stopped(self, runner, mock_service_fn) -> None:
        """_run_service sets status=started while running, stopped in finally."""

        statuses = []

        def capturing_fn(**_kwargs):
            """Capture the status and stop after the first iteration."""
            statuses.append(runner.service_runner_thread_status)
            runner.stop_event.set()  # Stop after first iteration
            return make_service_result(0.0)

        runner.service_function = capturing_fn
        runner._run_service(period_hours=1)

        assert "started" in statuses
        assert runner.service_runner_thread_status == "stopped"

    def test_sets_service_running_flag(self, runner) -> None:
        """service_running is True during the call, False after."""

        running_during = []

        def capturing_fn(**_kwargs):
            """Capture the status and stop after the first iteration."""
            running_during.append(runner.service_running)
            runner.stop_event.set()
            return make_service_result(0.0)

        runner.service_function = capturing_fn
        runner._run_service(period_hours=1)

        assert running_during == [True]
        assert runner.service_running is False

    def test_stop_event_breaks_loop(self, runner, mock_service_fn) -> None:
        """If stop_event is set during sleep, the loop exits cleanly."""

        call_count = 0

        def counting_fn(**_kwargs):
            """Call count is incremented after the first iteration."""
            nonlocal call_count
            call_count += 1
            runner.stop_event.set()
            return make_service_result(0.0)

        runner.service_function = counting_fn
        runner._run_service(period_hours=1)

        assert call_count == 1
        assert runner.service_runner_thread_status == "stopped"

    def test_exception_sets_service_running_false(self, runner) -> None:
        """If the service function raises, service_running is reset to False."""

        call_count = 0

        def raising_fn(**_kwargs):
            """Raise an exception after the first iteration."""
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("boom")
            runner.stop_event.set()
            return make_service_result(0.0)

        runner.service_function = raising_fn

        # Patch stop_event.wait so it returns True immediately (simulating stop during error recovery)
        original_wait = runner.stop_event.wait

        def fast_wait(timeout=None):
            """Fast wait that returns True immediately on the first call."""
            _ = timeout
            if call_count == 1:
                runner.stop_event.set()
                return True
            return original_wait(timeout=0)

        runner.stop_event.wait = fast_wait
        runner._run_service(period_hours=1)

        assert runner.service_running is False

    def test_sleep_tracking_cleared_after_wakeup(self, runner) -> None:
        """sleep_start / sleep_until are None after the service loop exits."""

        def one_shot_fn(**_kwargs):
            """Service function that exits after the first iteration."""
            runner.stop_event.set()
            return make_service_result(0.0)

        runner.service_function = one_shot_fn
        runner._run_service(period_hours=1)

        assert runner.sleep_start is None
        assert runner.sleep_until is None

    def test_service_kwargs_passed_to_function(self, runner) -> None:
        """service_kwargs are forwarded as keyword arguments to the service function."""

        received = {}

        def capturing_fn(**kwargs):
            """Capture the service kwargs and stop after the first iteration."""
            received.update(kwargs)
            runner.stop_event.set()
            return make_service_result(0.0)

        runner.service_kwargs = {"db": "mock_db", "user": "mock_user"}
        runner.service_function = capturing_fn
        runner._run_service(period_hours=1)

        assert received == {"db": "mock_db", "user": "mock_user"}

    def test_finally_always_sets_status_stopped_on_exception(self, runner) -> None:
        """Even if the loop exits due to an unexpected error, status becomes stopped."""

        def always_raises(**_kwargs):
            """Always raises an exception."""
            raise SystemExit(0)

        runner.service_function = always_raises

        with pytest.raises(SystemExit):
            runner._run_service(period_hours=1)

        assert runner.service_runner_thread_status == "stopped"


# -------------------------------------------------- STATUS ---------------------------------------------------


class TestStatus:

    def test_returns_expected_keys(self, runner) -> None:
        with patch("app.service_runner.service_runner.get_last_log_line", return_value=None):
            result = runner.status()

        expected_keys = {
            "service_runner_status",
            "service_running",
            "service_kwargs",
            "period_hours",
            "sleep_until",
            "last_log",
        }
        assert set(result.keys()) == expected_keys

    def test_reflects_current_state(self, runner) -> None:
        runner.service_runner_thread_status = "started"
        runner.service_running = True
        runner.sleep_until = 9999.0

        with patch("app.service_runner.service_runner.get_last_log_line", return_value="log line"):
            result = runner.status()

        assert result["service_runner_status"] == "started"
        assert result["service_running"] is True
        assert result["sleep_until"] == 9999.0
        assert result["last_log"] == "log line"

    def test_calls_get_last_log_line_with_service_name(self, runner) -> None:
        with patch("app.service_runner.service_runner.get_last_log_line") as mock_log:
            mock_log.return_value = None
            runner.status()

        mock_log.assert_called_once_with("test_svc")

    def test_service_kwargs_returned(self, runner) -> None:
        runner.service_kwargs = {"foo": "bar"}
        with patch("app.service_runner.service_runner.get_last_log_line", return_value=None):
            result = runner.status()
        assert result["service_kwargs"] == {"foo": "bar"}
