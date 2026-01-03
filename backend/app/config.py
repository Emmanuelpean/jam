"""JAM configuration"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database settings
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str

    # Authentication settings
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Application settings
    min_password_length: int
    max_file_size_mb: int
    log_directory: str

    # Email configuration
    email_username: str
    email_password: str
    email_smtp_port: int
    email_smtp_host: str
    email_imap_port: int
    email_imap_host: str
    scraper_email: str
    info_email: str
    support_email: str

    # URL configuration
    frontend_url: str
    backend_url: str

    # Verification settings
    verification_token_expiration_minutes: int
    verification_email_min_interval_seconds: int

    # Testing
    test_mode: bool

    # BrightAPI
    brightdata_api_key: str
    brightdata_linkedin_dataset_id: str
    brightdata_indeed_dataset_id: str

    # AI Keys
    openai_api_key: str

    # Apify
    apify_api_key: str

    # Stripe
    stripe_secret_key: str
    stripe_webhook_secret: str
    stripe_toast_price_id: str

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=Path(__file__).parent.parent / ".env",
    )


settings = Settings()  # type: ignore[call-arg]
