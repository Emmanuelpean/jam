"""Database models for application settings and user management."""

import datetime as dt
import math
from typing import Any

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, CheckConstraint, JSON, Text, event
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from enum import Enum

from app.base_models import CommonBase, Owned
from app.config import settings
from app.database import Base


class Setting(CommonBase, Base):
    """Represents the application settings

    Attributes:
    -----------
    - `name` (str, unique): The name of the setting.
    - `value` (float): The value of the setting.
    - `description` (str): A description of the setting.
    - `is_active` (bool): Indicates whether the setting is active."""

    name = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())


def get_setting_value(db, name: str, default: Any):
    """Retrieve a setting value from the database by its name.
    :param db: Database session.
    :param name: The name of the setting to retrieve.
    :param default: The default value to return if the setting is not found."""

    entry = db.query(Setting).filter(Setting.name == name).filter(Setting.is_active).first()
    if entry:
        return entry.value
    else:
        return default


class User(CommonBase, Base):
    """Represents core user identification and authentication.

    Attributes:
    -----------
    - `password` (str): Encrypted password for authentication.
    - `email` (str, unique): User's email address.
    - `is_active` (bool): Indicates whether the user account is active.
    - `is_admin` (bool): Indicates whether the user is an administrator.
    - `is_demo` (bool): Indicates whether the user is a demo account.
    - `is_verified` (bool): Indicates whether the user's email is verified.
    - `last_login` (datetime, optional): The timestamp of the last login.
    - `previous_login` (datetime, optional): The timestamp of the previous login.
    - `app_version` (str, optional): Version of the application used for the last login.
    - `first_name` (str, optional): User's first name.
    - `last_name` (str, optional): User's last name.
    - `token_version` (int): Version of the token for invalidation purposes.
    - `name` (str, optional): Computed property that combines first and last name.

    Relationships:
    --------------
    - `preferences` (UserPreferences): One-to-one relationship to user preferences.
    - `stripe_details` (StripeDetails): One-to-one relationship to Stripe payment details.
    - `premium` (PremiumSettings): One-to-one relationship to premium subscription settings.
    - `tokens` (list of UserToken): One-to-many relationship to user tokens."""

    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, server_default=expression.true())
    is_admin = Column(Boolean, nullable=False, server_default=expression.false())
    is_demo = Column(Boolean, nullable=False, server_default=expression.false())
    is_verified = Column(Boolean, nullable=False, server_default=expression.false())
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    previous_login = Column(TIMESTAMP(timezone=True), nullable=True)
    app_version = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    token_version = Column(Integer, default=0, nullable=False)

    # Relationships
    preferences = relationship("UserPreferences", uselist=False, cascade="all, delete-orphan", lazy="joined")
    stripe_details = relationship("StripeDetails", uselist=False, cascade="all, delete-orphan", lazy="joined")
    premium = relationship("PremiumSettings", uselist=False, cascade="all, delete-orphan", lazy="joined")
    tokens = relationship("UserToken", cascade="all, delete-orphan", lazy="dynamic")

    def __init__(self, **kwargs) -> None:
        """Initialise User with automatic creation of related records."""

        # Extract relationship data before calling super().__init__
        preferences_data = kwargs.pop("preferences", None)
        stripe_details_data = kwargs.pop("stripe_details", None)
        premium_data = kwargs.pop("premium", None)

        # Call parent constructor with remaining kwargs
        super().__init__(**kwargs)

        # Handle preferences - create an instance if dict provided or if not already set
        if preferences_data:
            if isinstance(preferences_data, dict):
                # noinspection PyArgumentList
                self.preferences = UserPreferences(**preferences_data)
            else:
                self.preferences = preferences_data
        elif not self.preferences:
            self.preferences = UserPreferences()

        # Handle stripe_details - create an instance if dict provided or if not already set
        if stripe_details_data:
            if isinstance(stripe_details_data, dict):
                # noinspection PyArgumentList
                self.stripe_details = StripeDetails(**stripe_details_data)
            else:
                self.stripe_details = stripe_details_data
        elif not self.stripe_details:
            self.stripe_details = StripeDetails()

        # Handle premium - create instance if dict provided or if not already set
        if premium_data:
            if isinstance(premium_data, dict):
                # noinspection PyArgumentList
                self.premium = PremiumSettings(**premium_data)
            else:
                self.premium = premium_data
        elif not self.premium:
            self.premium = PremiumSettings()

    @hybrid_property
    def name(self) -> str | None:
        """Computed property that combines the first and last name"""

        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return None

    @hybrid_property
    def pending_email_change(self) -> str | None:
        """Check if there is a pending email change token"""

        for token in self.tokens:
            if token.token_type == TokenType.EMAIL_CHANGE:
                return token.pending_email
        return None


class UserPreferences(Owned, Base):
    """User-specific preferences and settings.

    Attributes:
    -----------
    - `theme` (str): The theme of the application.
    - `dark_mode` (bool): Indicates whether dark mode is enabled.
    - `chase_threshold` (int): The threshold for chasing jobs in the dashboard.
    - `deadline_threshold` (int): The threshold for deadlines in the dashboard.
    - `update_limit` (int): Max number updates displayed in the dashboard.
    - `default_currency` (str): The default currency for salary fields."""

    theme = Column(String, nullable=False, server_default="mixed-berry")
    dark_mode = Column(String, nullable=False, server_default="system")
    chase_threshold = Column(Integer, nullable=False, server_default="14")
    deadline_threshold = Column(Integer, nullable=False, server_default="7")
    update_limit = Column(Integer, nullable=False, server_default="10")
    default_currency = Column(String, nullable=False, server_default="GBP")
    dashboard_layout = Column(Text, nullable=True)
    table_columns = Column(JSON, nullable=True)
    table_sort = Column(JSON, nullable=True)
    extension_banner_dismissed = Column(Boolean, nullable=False, server_default="false")
    completed_tours = Column(JSON, nullable=True)


class StripeDetails(Owned, Base):
    """Stripe payment and subscription information.

    Attributes:
    -----------
    - `customer_id` (str, optional): Stripe customer identifier.
    - `subscription_id` (str, optional): Stripe subscription identifier.
    - `subscription_status` (str, optional): Current subscription status.
    - `trial_end_date` (int, optional): Timestamp of trial end date in seconds since epoch."""

    customer_id = Column(String, nullable=True)
    subscription_id = Column(String, nullable=True)
    subscription_status = Column(String, nullable=True)
    trial_end_date = Column(Integer, nullable=True)


class PremiumSettings(Owned, Base):
    """Premium subscription settings and feature flags.

    Attributes:
    -----------
    - `is_active` (bool): Indicates whether the user has an active premium subscription.
    - `job_scraping_active` (bool): Indicates whether job scraping is enabled.
    - `job_rating_active` (bool): Indicates whether job rating is enabled."""

    is_active = Column(Boolean, nullable=False, server_default=expression.false())
    job_scraping_active = Column(Boolean, nullable=False, server_default=expression.true())
    job_rating_active = Column(Boolean, nullable=False, server_default=expression.true())


class TokenType(str, Enum):
    """User token type enum."""

    VERIFICATION = "verification"
    PASSWORD_RESET = "password_reset"
    EMAIL_CHANGE = "email_change"


class UserToken(Owned, Base):
    """Authentication and verification tokens.

    Attributes:
    -----------
    - `token` (str, unique): The actual token string.
    - `token_type` (str): Type of token (TokenType enum).
    - `pending_email` (str, optional): For email_change tokens, the new email address.
    - `is_valid` (bool): Computed property to check if the token is valid."""

    token = Column(String, nullable=False, unique=True, index=True)
    token_type = Column(String, nullable=False)
    pending_email = Column(String, nullable=True)

    @hybrid_property
    def is_valid(self) -> bool:
        """Check if the token is valid"""

        # Define expiration times based on the token type
        expiration_minutes = {
            TokenType.VERIFICATION: settings.verification_token_expiration_minutes,
            TokenType.PASSWORD_RESET: settings.password_reset_token_expiration_minutes,
            TokenType.EMAIL_CHANGE: settings.email_change_token_expiration_minutes,
        }

        # noinspection PyTypeChecker
        minutes = expiration_minutes.get(self.token_type, settings.verification_token_expiration_minutes)
        expiration_time = self.created_at + dt.timedelta(minutes=minutes)
        return dt.datetime.now(dt.timezone.utc) < expiration_time

    @hybrid_property
    def remaining_seconds(self) -> int:
        """Calculate how many seconds remain until the next email can be sent.
        :return: seconds remaining until next email can be sent"""

        time_since_last_email = int((dt.datetime.now(dt.timezone.utc) - self.created_at).total_seconds())
        return math.ceil(settings.verification_email_min_interval_seconds - time_since_last_email)


@event.listens_for(UserToken, "before_insert")
def delete_existing_tokens_of_same_type(mapper, connection, target):
    """Delete existing tokens of the same type for the same user before inserting a new one."""

    _ = mapper
    connection.execute(
        UserToken.__table__.delete().where(
            (UserToken.owner_id == target.owner_id) & (UserToken.token_type == target.token_type)
        )
    )


class UserQualification(Owned, Base):
    """User qualifications for job matching

    Attributes:
    -----------
    - `experience` (str): User's experience details.
    - `skills` (str): User's skills details.
    - `qualities` (str): User's personal qualities.
    - `education` (str): User's education details.
    - `interests` (str): User's job interests.

    Relationships:
    --------------
    - `job_ratings` (list of JobRating): List of job ratings associated with the user qualification.

    Constraints
    ------------
    - At least one of experience, skills, qualities, education, or interests must be provided"""

    experience = Column(String, nullable=True)
    skills = Column(String, nullable=True)
    qualities = Column(String, nullable=True)
    education = Column(String, nullable=True)
    interests = Column(String, nullable=True)

    job_ratings = relationship("JobRating", back_populates="user_qualification")

    __table_args__ = (
        CheckConstraint(
            "experience IS NOT NULL OR skills IS NOT NULL OR qualities IS NOT NULL OR education IS NOT NULL OR interests IS NOT NULL",
            name="user_qualification_data_required",
        ),
    )
