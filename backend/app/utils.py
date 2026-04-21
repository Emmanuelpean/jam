"""Module containing utility functions."""

import hashlib
import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import bcrypt
from pydantic import EmailStr

from app.config import settings


def hash_password(password: str, rounds: int = 12) -> str:
    """Hash a password for storing.
    :param password: password to hash
    :param rounds: number of bcrypt rounds (default: 12)
    :return: hashed password"""

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=rounds)).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a stored password against one provided by the user.
    :param password: raw password to check
    :param hashed: hashed password from the database
    :return: boolean indicating whether the passwords matched"""

    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def hash_token(token: str) -> str:
    """Hash a token for secure storage.
    :param token: token to hash
    :return: hashed token"""

    return hashlib.sha256(token.encode()).hexdigest()


def clean_email(email: EmailStr | str) -> str:
    """Normalise the email address by stripping whitespace and converting to lowercase.
    :param email: The email address to be cleaned
    :return: Cleaned email address"""

    return str(email).strip().lower()


def open_json(filepath: str) -> list[dict]:
    """Open a file and return its content
    :param filepath: The json file to open
    :return: The contents of the file"""

    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "..", filepath)
    with open(path, "r", encoding="utf8") as ofile:
        return json.load(ofile)


def super_getattr(obj: object, attr: str) -> object:
    """Get nested attributes from an object using dot notation.
    :param obj: The object to get attributes from
    :param attr: The attribute path in dot notation"""

    attrs = attr.split(".")
    for a in attrs:
        obj = getattr(obj, a)
    return obj


def super_hasattr(obj: object, attr: str) -> bool:
    """Check if nested attributes exist in an object using dot notation.
    :param obj: The object to check attributes from
    :param attr: The attribute path in dot notation"""

    attrs = attr.split(".")
    for a in attrs:
        if not hasattr(obj, a):
            return False
        obj = getattr(obj, a)
    return True


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
    ) -> logging.Logger:
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

        # Create new logger
        logger = logging.getLogger(name)
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
    def create_service_logger(cls, service_name: str, log_level: str = "INFO") -> logging.Logger:
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


def get_last_log_line(logger_name: str) -> str | None:
    """Get the last line from the service log file efficiently.
    Reads from the end of the file to avoid loading the entire file.
    :param logger_name: Name of the logger / log file"""

    log_file_path = os.path.join(settings.log_directory, logger_name + ".log")

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
