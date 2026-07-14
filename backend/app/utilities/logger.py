"""Centralised application logging: rotating-file loggers that can also read back their own log tails."""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, cast

from app.config import settings


class AppLoggerInstance(logging.Logger):
    """A logging.Logger extended with helpers to read back its own log file."""

    def _log_file_path(self) -> str:
        """Return the path of this logger's log file ({name}.log under the log directory)."""

        return os.path.join(settings.log_directory, self.name + ".log")

    def read_log_tail(self, lines: int) -> dict:
        """Return the last lines lines of this logger's log file plus the file's total line count.

        Reads the whole file for small files; for files over 1 MB it seeks from the end in chunks to
        avoid loading the entire file into memory.
        :param lines: Number of trailing lines to return.
        :return: {"lines": list[str], "total_lines": int}."""

        log_file_path = self._log_file_path()

        if not os.path.exists(log_file_path):
            return {"lines": [], "total_lines": 0}

        try:
            file_size = os.path.getsize(log_file_path)

            # For small files, just read the whole thing
            if file_size < 1024 * 1024:  # 1 MB threshold
                with open(log_file_path, "r", encoding="utf-8") as f:
                    all_lines = f.readlines()
                total_lines = len(all_lines)
                log_lines = all_lines[-lines:] if lines < total_lines else all_lines
                return {"lines": [line.rstrip() for line in log_lines], "total_lines": total_lines}

            # For large files, read from the end in chunks
            chunk_size = 8192
            collected_lines = []
            total_lines = 0

            with open(log_file_path, "rb") as f:
                # Count total lines efficiently
                for _ in f:
                    total_lines += 1

                # Now read from the end to get the last N lines
                f.seek(0, 2)  # Seek to end
                position = f.tell()
                buffer = b""

                while position > 0 and len(collected_lines) < lines:
                    read_size = min(chunk_size, position)
                    position -= read_size
                    f.seek(position)
                    chunk = f.read(read_size)
                    buffer = chunk + buffer

                    buffer_lines = buffer.split(b"\n")

                    # If we haven't reached the start, the first element is incomplete
                    if position > 0:
                        buffer = buffer_lines[0]
                        new_lines = buffer_lines[1:]
                    else:
                        new_lines = buffer_lines
                        buffer = b""

                    collected_lines = new_lines + collected_lines

                result_lines = collected_lines[-lines:] if len(collected_lines) > lines else collected_lines

                decoded_lines = []
                for line in result_lines:
                    try:
                        decoded_lines.append(line.decode("utf-8").rstrip())
                    except UnicodeDecodeError:
                        decoded_lines.append(line.decode("utf-8", errors="replace").rstrip())

                decoded_lines = [line for line in decoded_lines if line]

                return {"lines": decoded_lines, "total_lines": total_lines}

        except Exception as e:
            return {"lines": [f"Error reading log file: {str(e)}"], "total_lines": 0}

    def get_last_log_line(self) -> str | None:
        """Get the last line from this logger's log file efficiently.
        Reads from the end of the file to avoid loading the entire file."""

        log_file_path = self._log_file_path()

        if not os.path.exists(log_file_path):
            return None

        try:
            with open(log_file_path, "rb") as f:
                # Seek to end
                f.seek(0, 2)
                position = f.tell()

                if position == 0:
                    return None

                # Read backwards to find the last non-empty line
                chunk_size = 1024
                buffer = b""

                while position > 0:
                    read_size = min(chunk_size, position)
                    position -= read_size
                    f.seek(position)
                    buffer = f.read(read_size) + buffer

                    # Split and look for a complete line
                    lines = buffer.split(b"\n")

                    # Find the last non-empty line
                    for line in reversed(lines):
                        stripped = line.strip()
                        if stripped:
                            try:
                                return stripped.decode("utf-8")
                            except UnicodeDecodeError:
                                return stripped.decode("utf-8", errors="replace")

                return None

        except Exception as e:
            return f"Error reading log file: {str(e)}"


class AppLogger:
    """Centralised logging utility"""

    _loggers = {}  # Cache for created loggers

    @classmethod
    def get_logger(
        cls,
        name: str,
        log_file: Optional[str] = None,
        level: int = logging.INFO,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
    ) -> AppLoggerInstance:
        """Get or create a logger with the specified configuration
        :param name: Logger name (usually module name)
        :param log_file: Specific log file name (defaults to {name}.log)
        :param level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        :param max_file_size: Maximum size of log file before rotation
        :param backup_count: Number of backup files to keep
        :param console_output: Whether to output logs to console
        :return: Configured logger instance"""

        # Return cached logger if it exists
        log_dir = settings.log_directory
        cache_key = f"{name}_{log_dir}_{log_file}"
        if cache_key in cls._loggers:
            return cls._loggers[cache_key]

        # Create new logger (reclassed so it carries the log-reading helpers)
        base_logger = logging.getLogger(name)
        base_logger.__class__ = AppLoggerInstance
        logger = cast(AppLoggerInstance, base_logger)
        logger.setLevel(level)

        # Prevent duplicate handlers if logger already exists
        if logger.handlers:
            cls._loggers[cache_key] = logger
            return logger

        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # Set log file name
        if not log_file:
            log_file = f"{name}.log"

        full_log_path = log_path / log_file

        # Create formatters
        detailed_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        simple_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # File handler with rotation
        file_handler = RotatingFileHandler(
            full_log_path, maxBytes=max_file_size, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        # Console handler
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_handler.setFormatter(simple_formatter)
            logger.addHandler(console_handler)

        # Cache the logger
        cls._loggers[cache_key] = logger

        return logger

    @classmethod
    def read_logger(cls, name: str) -> AppLoggerInstance:
        """Return a read-only logger handle for name — no handlers, no file created.
        :param name: Logger / log-file name."""

        return AppLoggerInstance(name)

    @classmethod
    def create_service_logger(cls, service_name: str, log_level: str = "INFO") -> AppLoggerInstance:
        """Create a standardised logger for a service
        :param service_name: Name of the service (e.g., 'gmail_scraper', 'job_scraper')
        :param log_level: String representation of log level
        :return: Configured logger"""

        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        level = level_map.get(log_level.upper(), logging.INFO)

        return cls.get_logger(
            name=service_name,
            log_file=f"{service_name}.log",
            level=level,
            max_file_size=10 * 1024 * 1024,  # 10MB
            backup_count=5,
            console_output=True,
        )
