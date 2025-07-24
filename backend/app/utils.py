"""Module containing utility functions."""

import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import bcrypt


def hash_password(password: str) -> str:
    """Hash a password for storing.
    :param password: password to hash"""

    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a stored password against one provided by user.
    :param password: password to check against
    :param hashed: hashed password from database
    :return: boolean indicating whether password matched"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


class AppLogger:
    """Centralized logging utility for the application"""

    _loggers = {}  # Cache for created loggers

    @classmethod
    def get_logger(
        cls,
        name: str,
        log_dir: str = "logs",
        log_file: Optional[str] = None,
        level: int = logging.INFO,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        console_output: bool = True,
    ) -> logging.Logger:
        """
        Get or create a logger with the specified configuration

        :param name: Logger name (usually module name)
        :param log_dir: Directory for log files
        :param log_file: Specific log file name (defaults to {name}.log)
        :param level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        :param max_file_size: Maximum size of log file before rotation
        :param backup_count: Number of backup files to keep
        :param console_output: Whether to output logs to console
        :return: Configured logger instance
        """

        # Return cached logger if it exists
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
        """
        Create a standardized logger for a service

        :param service_name: Name of the service (e.g., 'gmail_scraper', 'job_scraper')
        :param log_level: String representation of log level
        :return: Configured logger
        """

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
            log_dir="logs",
            log_file=f"{service_name}.log",
            level=level,
            max_file_size=10 * 1024 * 1024,  # 10MB
            backup_count=5,
            console_output=True,
        )

    @classmethod
    def log_execution_time(cls, logger: logging.Logger, start_time: datetime, operation: str):
        """
        Log execution time for an operation

        :param logger: Logger instance
        :param start_time: Start time of the operation
        :param operation: Description of the operation
        """
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"{operation} completed in {duration.total_seconds():.2f} seconds")

    @classmethod
    def log_stats(cls, logger: logging.Logger, stats: dict, title: str = "Operation Statistics"):
        """
        Log statistics in a formatted way

        :param logger: Logger instance
        :param stats: Dictionary of statistics
        :param title: Title for the statistics block
        """
        logger.info("=" * 50)
        logger.info(title)
        logger.info("=" * 50)

        for key, value in stats.items():
            if isinstance(value, list):
                logger.info(f"{key}: {len(value)} items")
                if value:  # Log first few items if list is not empty
                    sample = value[:3]
                    logger.debug(f"  Sample {key}: {sample}")
            else:
                logger.info(f"{key}: {value}")

        logger.info("=" * 50)


def get_gmail_logger() -> logging.Logger:
    """Get logger for Gmail scraping service"""
    return AppLogger.create_service_logger("gmail_scraper", "INFO")


def get_job_scraper_logger() -> logging.Logger:
    """Get logger for job scraping service"""
    return AppLogger.create_service_logger("job_scraper", "INFO")


def get_scheduler_logger() -> logging.Logger:
    """Get logger for scheduler service"""
    return AppLogger.create_service_logger("scheduler", "INFO")


def get_api_logger() -> logging.Logger:
    """Get logger for API operations"""
    return AppLogger.create_service_logger("api", "INFO")


def get_database_logger() -> logging.Logger:
    """Get logger for database operations"""
    return AppLogger.create_service_logger("database", "WARNING")  # Less verbose for DB


def get_auth_logger() -> logging.Logger:
    """Get logger for authentication operations"""
    return AppLogger.create_service_logger("auth", "INFO")
