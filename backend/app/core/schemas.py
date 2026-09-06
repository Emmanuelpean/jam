"""Schemas for the JAM database
Create schemas should be used to create entries in the database.
Out schemas should be used to return data to the user.
Min schemas should be used to return minimal data to the user (enough to display the entry as a badge) and should not
contain reference to other tables.
Update schemas should be used to update existing entries in the database."""

import datetime as dt
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.base_schemas import Out, OwnedOut, EmailField, ColumnLimits, COLUMN_LIMITS

# ------------------------------------------------------- SETTINGS ------------------------------------------------------


class SettingCreate(BaseModel):
    """Setting create schema"""

    name: str
    value: str
    description: str | None = None
    is_active: bool = True


class SettingOut(SettingCreate, Out):
    """Setting output schema"""

    pass


class SettingUpdate(SettingCreate):
    """Keyword update schema"""

    name: str | None = None
    value: str | None = None


# ------------------------------------------------------ REGISTER ------------------------------------------------------


class UserRegister(BaseModel):
    """User create schema"""

    email: EmailField
    password: str = Field(max_length=COLUMN_LIMITS.password)
    first_name: str = Field(max_length=COLUMN_LIMITS.first_name)
    last_name: str = Field(max_length=COLUMN_LIMITS.last_name)
    captcha_token: str = Field(default="", max_length=4096)


# -------------------------------------------------------- LOGIN -------------------------------------------------------


class UserLogin(BaseModel):
    """User login schema"""

    email: EmailField
    password: str = Field(max_length=COLUMN_LIMITS.password)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None
    token_version: int = 0
    is_demo: bool = False


# ------------------------------------------------- USER PREFERENCES ---------------------------------------------------


ThemeMode = Literal["dark", "light", "system"]

TourId = Annotated[str, Field(max_length=COLUMN_LIMITS.tour_id)]
EntityType = Annotated[str, Field(max_length=COLUMN_LIMITS.table_entity_type)]
ColumnName = Annotated[str, Field(max_length=COLUMN_LIMITS.table_column_key)]
_ColumnList = Annotated[list[ColumnName], Field(max_length=COLUMN_LIMITS.table_columns)]
_SortEntryValue = Annotated[str, Field(max_length=COLUMN_LIMITS.table_sort_value)]
_SortEntry = Annotated[dict[str, _SortEntryValue], Field(max_length=COLUMN_LIMITS.table_sort_entry_keys)]
_PageSize = Annotated[int, Field(ge=1, le=COLUMN_LIMITS.table_page_size_max)]


class UserPreferencesCreate(BaseModel):
    """User preferences create schema
    Defaults are handled in the database layer."""

    theme: str | None = Field(default=None, max_length=COLUMN_LIMITS.theme)
    dark_mode: ThemeMode = Field(default="system", max_length=COLUMN_LIMITS.theme_mode)
    default_currency: str | None = None
    extension_banner_dismissed: bool = False
    completed_tours: list[TourId] | None = Field(default=None, max_length=COLUMN_LIMITS.completed_tours)
    tour_panel_dismissed: bool = False
    dashboard_layout: str | None = Field(default=None, max_length=COLUMN_LIMITS.dashboard_layout)
    table_columns: dict[EntityType, _ColumnList] | None = Field(
        default=None, max_length=COLUMN_LIMITS.table_entity_types
    )
    table_sort: dict[EntityType, _SortEntry] | None = Field(default=None, max_length=COLUMN_LIMITS.table_entity_types)
    table_page_size: dict[EntityType, _PageSize] | None = Field(
        default=None, max_length=COLUMN_LIMITS.table_entity_types
    )


class UserPreferencesUpdate(UserPreferencesCreate):
    """User preferences update schema"""

    pass


class UserPreferencesOut(Out, UserPreferencesUpdate):
    """User preferences output schema"""

    pass


# --------------------------------------------------- PREMIUM DETAILS --------------------------------------------------


class PremiumDetailsCreate(BaseModel):
    """Premium details create schema"""

    is_active: bool = False
    job_scraping_active: bool = True
    job_rating_active: bool = True


class PremiumDetailsOut(PremiumDetailsCreate, Out):
    """Premium details output schema"""

    pass


class PremiumDetailsUpdate(PremiumDetailsCreate):
    """Premium details update schema"""

    pass


class CurrentUserPremiumDetailsUpdate(BaseModel):
    """Premium details update schema"""

    job_scraping_active: bool | None = None
    job_rating_active: bool | None = None


# ------------------------------------------------------- STRIPE -------------------------------------------------------


class StripeDetails(BaseModel):
    """Stripe details schema"""

    subscription_status: str | None = None
    trial_end_date: int | None = None


# -------------------------------------------------------- USERS -------------------------------------------------------


class UserCreate(BaseModel):
    """User create schema for the admin endpoint"""

    email: EmailField
    password: str = Field(max_length=COLUMN_LIMITS.password)
    is_active: bool = True
    is_admin: bool = False
    is_demo: bool = False
    first_name: str | None = Field(default=None, max_length=COLUMN_LIMITS.first_name)
    last_name: str | None = Field(default=None, max_length=COLUMN_LIMITS.last_name)
    premium: PremiumDetailsCreate | None = None
    preferences: UserPreferencesCreate | None = None


class UserOut(Out):
    """User output schema for the admin endpoint"""

    email: EmailField
    is_active: bool
    is_admin: bool
    is_demo: bool
    is_verified: bool
    last_login: dt.datetime | None
    previous_login: dt.datetime | None
    app_version: str | None
    first_name: str | None = None
    last_name: str | None = None
    name: str | None = None
    token_version: int
    pending_email_change: str | None
    preferences: UserPreferencesOut | None
    premium: PremiumDetailsOut | None
    stripe_details: StripeDetails | None


class UserUpdate(BaseModel):
    """User account update schema for the admin endpoint"""

    email: EmailField | None = None
    password: str | None = Field(default=None, max_length=COLUMN_LIMITS.password)
    is_active: bool = True
    is_admin: bool = False
    is_demo: bool = False
    first_name: str | None = Field(default=None, max_length=COLUMN_LIMITS.first_name)
    last_name: str | None = Field(default=None, max_length=COLUMN_LIMITS.last_name)
    preferences: UserPreferencesUpdate | None = None
    premium: PremiumDetailsUpdate | None = None


class CurrentUserUpdate(BaseModel):
    """User account update schema for non-sensitive profile fields"""

    first_name: str | None = Field(default=None, max_length=COLUMN_LIMITS.first_name)
    last_name: str | None = Field(default=None, max_length=COLUMN_LIMITS.last_name)
    app_version: str | None = Field(default=None, max_length=COLUMN_LIMITS.app_version)
    preferences: UserPreferencesUpdate | None = None
    premium: CurrentUserPremiumDetailsUpdate | None = None


class CurrentUserPasswordUpdate(BaseModel):
    """Schema for the current user's password change"""

    current_password: str = Field(max_length=COLUMN_LIMITS.password)
    new_password: str = Field(max_length=COLUMN_LIMITS.password)


class CurrentUserEmailUpdate(BaseModel):
    """Schema for the current user's email change request"""

    email: EmailField
    current_password: str = Field(max_length=COLUMN_LIMITS.password)


# ------------------------------------------------- USER QUALIFICATIONS ------------------------------------------------


class UserQualificationUpsert(BaseModel):
    """User qualification create schema"""

    id: int | None = None
    experience: str | None = Field(default=None, max_length=COLUMN_LIMITS.experience)
    skills: str | None = Field(default=None, max_length=COLUMN_LIMITS.skills)
    education: str | None = Field(default=None, max_length=COLUMN_LIMITS.education)
    qualities: str | None = Field(default=None, max_length=COLUMN_LIMITS.qualities)
    interests: str | None = Field(default=None, max_length=COLUMN_LIMITS.interests)


class UserQualificationOut(UserQualificationUpsert, OwnedOut):
    """User qualification output schema"""

    pass


# --------------------------------------------------- PASSWORD RESET ---------------------------------------------------


class PasswordResetRequest(BaseModel):
    """Email request schema for password reset"""

    email: EmailField


class PasswordReset(BaseModel):
    """Password reset schema"""

    token: str = Field(max_length=COLUMN_LIMITS.token)
    new_password: str = Field(max_length=COLUMN_LIMITS.password)


# ---------------------------------------------------- EMAIL CHANGE ----------------------------------------------------


class CheckPendingEmailResponse(BaseModel):
    """Response for checking pending email"""

    has_pending_email: bool
    pending_email: str | None = None


# -------------------------------------------------- ACCOUNT DELETION --------------------------------------------------


class AccountDeleteRequest(BaseModel):
    """Account deletion request schema"""

    password: str = Field(max_length=COLUMN_LIMITS.password)


# ---------------------------------------------------- APP CONFIG -------------------------------------------------------


class ConfigOut(BaseModel):
    """Application configuration output schema"""

    scraper_email: str
    support_email: str
    platform_sender_emails: dict[str, str]
    min_password_length: int
    app_demo_username: str
    scrape_max_retry: int
    max_file_size_mb: int
    monthly_scrape_quota: int
    turnstile_site_key: str
    column_limits: ColumnLimits
