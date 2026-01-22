"""JAM configuration"""

import os
import tomllib
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_app_version() -> str:
    """Get the version of the application"""

    BASE_DIR = os.path.dirname(__file__)
    path = os.path.join(BASE_DIR, "../pyproject.toml")
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    return data["project"]["version"]


class Settings(BaseSettings):
    # Database settings
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

    # JWT settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Application settings
    app_version: str = get_app_version()
    max_file_size_mb: int

    # Other settings
    log_directory: str
    test_mode: bool

    # Email configuration
    main_email_username: str
    main_email_password: str
    scraper_email_username: str
    scraper_email_password: str
    email_smtp_port: int
    email_smtp_host: str
    email_imap_port: int
    email_imap_host: str
    info_email: str
    support_email: str

    # URL configuration
    frontend_url: str
    backend_url: str

    # Verification settings
    verification_token_expiration_minutes: int
    password_reset_token_expiration_minutes: int
    email_change_token_expiration_minutes: int
    verification_email_min_interval_seconds: int

    # BrightData
    brightdata_api_key: str
    brightdata_linkedin_dataset_id: str
    brightdata_indeed_dataset_id: str

    # OpenAI
    openai_api_key: str

    # Apify
    apify_api_key: str

    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str
    stripe_toast_price_id: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
    )


settings = Settings()  # type: ignore[call-arg]
