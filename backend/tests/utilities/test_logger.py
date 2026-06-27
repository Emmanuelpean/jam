"""Tests for utility functions."""

from unittest.mock import patch

from app.utilities.logger import AppLogger


class TestGetLastLogLine:

    def test_returns_none_when_file_does_not_exist(self, tmp_path) -> None:
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = AppLogger.read_logger("nonexistent").get_last_log_line()
        assert result is None

    def test_returns_none_for_empty_file(self, tmp_path) -> None:
        log_file = tmp_path / "empty.log"
        # noinspection PyTypeChecker
        log_file.write_bytes(b"")
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = AppLogger.read_logger("empty").get_last_log_line()
        assert result is None

    def test_returns_last_line_of_single_line_file(self, tmp_path) -> None:
        log_file = tmp_path / "single.log"
        log_file.write_text("only line\n", encoding="utf-8")
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = AppLogger.read_logger("single").get_last_log_line()
        assert result == "only line"

    def test_returns_last_line_of_multi_line_file(self, tmp_path) -> None:
        log_file = tmp_path / "multi.log"
        log_file.write_text("first line\nsecond line\nthird line\n", encoding="utf-8")
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = AppLogger.read_logger("multi").get_last_log_line()
        assert result == "third line"

    def test_ignores_trailing_blank_lines(self, tmp_path) -> None:
        log_file = tmp_path / "trailing.log"
        log_file.write_text("first line\nlast real line\n\n\n", encoding="utf-8")
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = AppLogger.read_logger("trailing").get_last_log_line()
        assert result == "last real line"

    def test_returns_none_for_whitespace_only_file(self, tmp_path) -> None:
        log_file = tmp_path / "whitespace.log"
        log_file.write_text("\n\n\n   \n", encoding="utf-8")
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = AppLogger.read_logger("whitespace").get_last_log_line()
        assert result is None

    def test_handles_file_larger_than_chunk_size(self, tmp_path) -> None:
        log_file = tmp_path / "large.log"
        # Write enough lines to exceed the 1024-byte chunk size
        lines = [f"log line number {i}" for i in range(100)]
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = AppLogger.read_logger("large").get_last_log_line()
        assert result == "log line number 99"

    def test_returns_error_string_on_read_failure(self, tmp_path) -> None:
        log_file = tmp_path / "unreadable.log"
        log_file.write_text("some content\n", encoding="utf-8")
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            with patch("builtins.open", side_effect=PermissionError("access denied")):
                result = AppLogger.read_logger("unreadable").get_last_log_line()
        assert result is not None
        assert "Error reading log file" in result

    def test_handles_unicode_content(self, tmp_path) -> None:
        log_file = tmp_path / "unicode.log"
        log_file.write_text("first line\nlast line with unicode: café\n", encoding="utf-8")
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = AppLogger.read_logger("unicode").get_last_log_line()
        assert result == "last line with unicode: café"

    def test_file_without_trailing_newline(self, tmp_path) -> None:
        log_file = tmp_path / "no_newline.log"
        log_file.write_text("first line\nlast line no newline", encoding="utf-8")
        with patch("app.utilities.logger.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = AppLogger.read_logger("no_newline").get_last_log_line()
        assert result == "last line no newline"
