"""Tests for utility functions."""

import logging
from collections.abc import Iterator
from logging.handlers import RotatingFileHandler
from pathlib import Path
from unittest.mock import patch

import pytest

from app.utilities.logger import AppLogger, AppLoggerInstance


@pytest.fixture
def log_dir(tmp_path: Path) -> Iterator[Path]:
    """Patch settings.log_directory to a temp dir and clean up any loggers/handlers created.

    Closing file handlers on teardown is required on Windows so tmp_path can be removed, and
    restoring AppLogger._loggers keeps the module-level cache from leaking between tests."""

    cache_before = dict(AppLogger._loggers)
    names_before = set(logging.Logger.manager.loggerDict.keys())
    with patch("app.utilities.logger.settings") as mock_settings:
        mock_settings.log_directory = str(tmp_path)
        yield tmp_path
    AppLogger._loggers.clear()
    AppLogger._loggers.update(cache_before)
    for name in set(logging.Logger.manager.loggerDict.keys()) - names_before:
        created = logging.getLogger(name)
        for handler in list(created.handlers):
            handler.close()
            created.removeHandler(handler)
        created.__class__ = logging.Logger


class TestGetLastLogLine:

    def test_returns_none_when_file_does_not_exist(self, log_dir: Path) -> None:
        result = AppLogger.read_logger("nonexistent").get_last_log_line()
        assert result is None

    def test_returns_none_for_empty_file(self, log_dir: Path) -> None:
        (log_dir / "empty.log").write_bytes(b"")
        result = AppLogger.read_logger("empty").get_last_log_line()
        assert result is None

    def test_returns_last_line_of_single_line_file(self, log_dir: Path) -> None:
        (log_dir / "single.log").write_text("only line\n", encoding="utf-8")
        result = AppLogger.read_logger("single").get_last_log_line()
        assert result == "only line"

    def test_returns_last_line_of_multi_line_file(self, log_dir: Path) -> None:
        (log_dir / "multi.log").write_text("first line\nsecond line\nthird line\n", encoding="utf-8")
        result = AppLogger.read_logger("multi").get_last_log_line()
        assert result == "third line"

    def test_ignores_trailing_blank_lines(self, log_dir: Path) -> None:
        (log_dir / "trailing.log").write_text("first line\nlast real line\n\n\n", encoding="utf-8")
        result = AppLogger.read_logger("trailing").get_last_log_line()
        assert result == "last real line"

    def test_returns_none_for_whitespace_only_file(self, log_dir: Path) -> None:
        (log_dir / "whitespace.log").write_text("\n\n\n   \n", encoding="utf-8")
        result = AppLogger.read_logger("whitespace").get_last_log_line()
        assert result is None

    def test_handles_file_larger_than_chunk_size(self, log_dir: Path) -> None:
        # Write enough lines to exceed the 1024-byte chunk size
        lines = [f"log line number {i}" for i in range(100)]
        (log_dir / "large.log").write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = AppLogger.read_logger("large").get_last_log_line()
        assert result == "log line number 99"

    def test_returns_error_string_on_read_failure(self, log_dir: Path) -> None:
        (log_dir / "unreadable.log").write_text("some content\n", encoding="utf-8")
        with patch("builtins.open", side_effect=PermissionError("access denied")):
            result = AppLogger.read_logger("unreadable").get_last_log_line()
        assert result is not None
        assert "Error reading log file" in result

    def test_handles_unicode_content(self, log_dir: Path) -> None:
        (log_dir / "unicode.log").write_text("first line\nlast line with unicode: café\n", encoding="utf-8")
        result = AppLogger.read_logger("unicode").get_last_log_line()
        assert result == "last line with unicode: café"

    def test_file_without_trailing_newline(self, log_dir: Path) -> None:
        (log_dir / "no_newline.log").write_text("first line\nlast line no newline", encoding="utf-8")
        result = AppLogger.read_logger("no_newline").get_last_log_line()
        assert result == "last line no newline"

    def test_decodes_invalid_utf8_with_replacement(self, log_dir: Path) -> None:
        # The last non-empty line is not valid UTF-8, exercising the replacement fallback.
        # noinspection PyTypeChecker
        (log_dir / "badutf8.log").write_bytes(b"good line\n\xff\xfe\n")
        result = AppLogger.read_logger("badutf8").get_last_log_line()
        assert result is not None
        assert "�" in result


class TestReadLogTail:

    def test_returns_empty_when_file_does_not_exist(self, log_dir: Path) -> None:
        result = AppLogger.read_logger("missing").read_log_tail(10)
        assert result == {"lines": [], "total_lines": 0}

    def test_small_file_returns_last_n_lines(self, log_dir: Path) -> None:
        (log_dir / "small.log").write_text("line1\nline2\nline3\nline4\n", encoding="utf-8")
        result = AppLogger.read_logger("small").read_log_tail(2)
        assert result == {"lines": ["line3", "line4"], "total_lines": 4}

    def test_small_file_returns_all_when_requested_exceeds_total(self, log_dir: Path) -> None:
        (log_dir / "small_all.log").write_text("line1\nline2\n", encoding="utf-8")
        result = AppLogger.read_logger("small_all").read_log_tail(10)
        assert result == {"lines": ["line1", "line2"], "total_lines": 2}

    def test_large_file_reads_from_end(self, log_dir: Path) -> None:
        log_file = log_dir / "big.log"
        # Exceed the 1 MB threshold so the chunked-from-end branch is used.
        lines = [f"log line number {i}" for i in range(100_000)]
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert log_file.stat().st_size > 1024 * 1024
        result = AppLogger.read_logger("big").read_log_tail(5)
        assert result["total_lines"] == 100_000
        # The returned lines are the contiguous tail of the file, ending at the final line.
        assert result["lines"][-1] == "log line number 99999"
        expected_tail = [f"log line number {i}" for i in range(100_000 - len(result["lines"]), 100_000)]
        assert result["lines"] == expected_tail

    def test_large_file_requesting_more_than_total_returns_all(self, log_dir: Path) -> None:
        log_file = log_dir / "big_all.log"
        lines = [f"row {i}" for i in range(130_000)]
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        assert log_file.stat().st_size > 1024 * 1024
        # Requesting more lines than exist forces the reader back to the start of the file.
        result = AppLogger.read_logger("big_all").read_log_tail(300_000)
        assert result["total_lines"] == 130_000
        assert result["lines"][0] == "row 0"
        assert result["lines"][-1] == "row 129999"
        assert len(result["lines"]) == 130_000

    def test_large_file_decodes_invalid_utf8(self, log_dir: Path) -> None:
        log_file = log_dir / "big_badutf8.log"
        # >1 MB of valid lines followed by a final line that is not valid UTF-8.
        # noinspection PyTypeChecker
        log_file.write_bytes(b"padding line\n" * 90_000 + b"\xff\xfe\n")
        assert log_file.stat().st_size > 1024 * 1024
        result = AppLogger.read_logger("big_badutf8").read_log_tail(2)
        assert "�" in result["lines"][-1]

    def test_returns_error_entry_on_read_failure(self, log_dir: Path) -> None:
        (log_dir / "boom.log").write_text("content\n", encoding="utf-8")
        with patch("builtins.open", side_effect=PermissionError("denied")):
            result = AppLogger.read_logger("boom").read_log_tail(5)
        assert result["total_lines"] == 0
        assert len(result["lines"]) == 1
        assert "Error reading log file" in result["lines"][0]


class TestGetLogger:

    def test_creates_file_and_console_handlers(self, log_dir: Path) -> None:
        logger = AppLogger.get_logger("ut_create", console_output=True)
        logger.info("hello world")
        assert any(isinstance(h, RotatingFileHandler) for h in logger.handlers)
        assert any(type(h) is logging.StreamHandler for h in logger.handlers)
        assert (log_dir / "ut_create.log").exists()
        assert "hello world" in (log_dir / "ut_create.log").read_text(encoding="utf-8")

    def test_console_output_false_skips_console_handler(self, log_dir: Path) -> None:
        logger = AppLogger.get_logger("ut_no_console", console_output=False)
        assert any(isinstance(h, RotatingFileHandler) for h in logger.handlers)
        assert not [h for h in logger.handlers if type(h) is logging.StreamHandler]

    def test_returns_cached_instance(self, log_dir: Path) -> None:
        first = AppLogger.get_logger("ut_cached")
        second = AppLogger.get_logger("ut_cached")
        assert first is second

    def test_reuses_existing_handlers_when_cache_cleared(self, log_dir: Path) -> None:
        first = AppLogger.get_logger("ut_reuse")
        handler_count = len(first.handlers)
        AppLogger._loggers.clear()  # drop the cache but keep the underlying logger's handlers
        second = AppLogger.get_logger("ut_reuse")
        assert second is first
        assert len(second.handlers) == handler_count  # no duplicate handlers added
        assert any(k.startswith("ut_reuse_") for k in AppLogger._loggers)

    def test_custom_log_file_name(self, log_dir: Path) -> None:
        AppLogger.get_logger("ut_named", log_file="custom.log")
        assert (log_dir / "custom.log").exists()


class TestReadLogger:

    def test_returns_instance_without_handlers(self, log_dir: Path) -> None:
        logger = AppLogger.read_logger("ut_readonly")
        assert isinstance(logger, AppLoggerInstance)
        assert logger.name == "ut_readonly"
        assert logger.handlers == []
        # Reading is a no-op that must not create the underlying file.
        assert not (log_dir / "ut_readonly.log").exists()


class TestCreateServiceLogger:

    @pytest.mark.parametrize(
        "level_str,expected",
        [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("CRITICAL", logging.CRITICAL),
            ("debug", logging.DEBUG),  # case-insensitive
        ],
    )
    def test_maps_level_string(self, log_dir: Path, level_str: str, expected: int) -> None:
        logger = AppLogger.create_service_logger(f"ut_svc_{level_str.lower()}", level_str)
        assert logger.level == expected

    def test_unknown_level_defaults_to_info(self, log_dir: Path) -> None:
        logger = AppLogger.create_service_logger("ut_svc_unknown", "VERBOSE")
        assert logger.level == logging.INFO

    def test_creates_named_log_file(self, log_dir: Path) -> None:
        AppLogger.create_service_logger("ut_svc_file")
        assert (log_dir / "ut_svc_file.log").exists()
