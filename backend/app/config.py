"""JAM configuration"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    signup: str
    min_password_length: int
    max_file_size_mb: int

    class Config:
        """Configuration for settings"""

        env_file = Path(__file__).parent.parent / ".env"


# noinspection PyArgumentList
settings = Settings()
