"""Tests for utility functions."""

from unittest.mock import patch

from app.utils import get_last_log_line, hash_password, verify_password


class TestPasswordUtils:

    def test_hash_is_not_plaintext(self) -> None:
        """Check that hashed password is not plaintext."""

        password = "securepassword"
        hashed = hash_password(password)
        assert hashed != password
        assert isinstance(hashed, str)

    def test_correct_password_verifies(self) -> None:
        """Check that correct password verifies."""

        password = "anothersecurepassword"
        hashed = hash_password(password)
        assert verify_password(password, hashed)

    def test_incorrect_password_fails(self) -> None:
        """Check that incorrect password fails."""

        password = "correcthorsebatterystaple"
        wrong_password = "correcthorsecarrotstaple"
        hashed = hash_password(password)
        assert not verify_password(wrong_password, hashed)

    def test_hash_is_unique_due_to_salt(self) -> None:
        """Check that hash is unique due to salt."""

        password = "saltypassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2  # because bcrypt adds salt
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestGetLastLogLine:

    def test_returns_none_when_file_does_not_exist(self, tmp_path) -> None:
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = get_last_log_line("nonexistent")
        assert result is None

    def test_returns_none_for_empty_file(self, tmp_path) -> None:
        log_file = tmp_path / "empty.log"
        log_file.write_bytes(b"")
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = get_last_log_line("empty")
        assert result is None

    def test_returns_last_line_of_single_line_file(self, tmp_path) -> None:
        log_file = tmp_path / "single.log"
        log_file.write_text("only line\n", encoding="utf-8")
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = get_last_log_line("single")
        assert result == "only line"

    def test_returns_last_line_of_multi_line_file(self, tmp_path) -> None:
        log_file = tmp_path / "multi.log"
        log_file.write_text("first line\nsecond line\nthird line\n", encoding="utf-8")
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = get_last_log_line("multi")
        assert result == "third line"

    def test_ignores_trailing_blank_lines(self, tmp_path) -> None:
        log_file = tmp_path / "trailing.log"
        log_file.write_text("first line\nlast real line\n\n\n", encoding="utf-8")
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = get_last_log_line("trailing")
        assert result == "last real line"

    def test_returns_none_for_whitespace_only_file(self, tmp_path) -> None:
        log_file = tmp_path / "whitespace.log"
        log_file.write_text("\n\n\n   \n", encoding="utf-8")
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = get_last_log_line("whitespace")
        assert result is None

    def test_handles_file_larger_than_chunk_size(self, tmp_path) -> None:
        log_file = tmp_path / "large.log"
        # Write enough lines to exceed the 1024-byte chunk size
        lines = [f"log line number {i}" for i in range(100)]
        log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = get_last_log_line("large")
        assert result == "log line number 99"

    def test_returns_error_string_on_read_failure(self, tmp_path) -> None:
        log_file = tmp_path / "unreadable.log"
        log_file.write_text("some content\n", encoding="utf-8")
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            with patch("builtins.open", side_effect=PermissionError("access denied")):
                result = get_last_log_line("unreadable")
        assert result is not None
        assert "Error reading log file" in result

    def test_handles_unicode_content(self, tmp_path) -> None:
        log_file = tmp_path / "unicode.log"
        log_file.write_text("first line\nlast line with unicode: café\n", encoding="utf-8")
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = get_last_log_line("unicode")
        assert result == "last line with unicode: café"

    def test_file_without_trailing_newline(self, tmp_path) -> None:
        log_file = tmp_path / "no_newline.log"
        log_file.write_text("first line\nlast line no newline", encoding="utf-8")
        with patch("app.utils.settings") as mock_settings:
            mock_settings.log_directory = str(tmp_path)
            result = get_last_log_line("no_newline")
        assert result == "last line no newline"
