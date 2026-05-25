"""Schemas for the JAM database
Create schemas should be used to create entries in the database.
Out schemas should be used to return data to the user.
Min schemas should be used to return minimal data to the user (enough to display the entry as a badge) and should not
contain reference to other tables.
Update schemas should be used to update existing entries in the database."""

import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ThemeMode = Literal["dark", "light", "system"]

from app.base_schemas import Out, OwnedOut, EmailField


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
    password: str = Field(max_length=128)
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)


# -------------------------------------------------------- LOGIN -------------------------------------------------------


class UserLogin(BaseModel):
    """User login schema"""

    email: EmailField
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str | None = None
    token_version: int = 0
    is_demo: bool = False


# ------------------------------------------------- USER PREFERENCES ---------------------------------------------------


class UserPreferencesCreate(BaseModel):
    """User preferences create schema
    Defaults are handled in the database layer."""

    theme: str | None = None
    dark_mode: ThemeMode = "system"
    chase_threshold: int | None = None
    deadline_threshold: int | None = None
    update_limit: int | None = None
    default_currency: str | None = None
    extension_banner_dismissed: bool | None = None
    completed_tours: list[str] | None = None
    dashboard_layout: str | None = None
    table_columns: dict[str, list[str]] | None = None
    table_sort: dict[str, dict[str, str]] | None = None


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
    password: str
    is_active: bool = True
    is_admin: bool = False
    is_demo: bool = False
    first_name: str | None = None
    last_name: str | None = None
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
    password: str | None = None
    is_active: bool = True
    is_admin: bool = False
    is_demo: bool = False
    first_name: str | None = None
    last_name: str | None = None
    preferences: UserPreferencesUpdate | None = None
    premium: PremiumDetailsUpdate | None = None


class CurrentUserUpdate(BaseModel):
    """User account update schema"""

    email: EmailField | None = None
    current_password: str | None = Field(default=None, max_length=128)
    password: str | None = Field(default=None, max_length=128)
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    app_version: str | None = Field(default=None, max_length=20)
    preferences: UserPreferencesUpdate | None = None
    premium: CurrentUserPremiumDetailsUpdate | None = None


class CurrentUserUpdateResponse(BaseModel):
    success: bool
    message: str
    logged_out: bool | None = None


# ------------------------------------------------- USER QUALIFICATIONS ------------------------------------------------


class UserQualificationUpsert(BaseModel):
    """User qualification create schema"""

    id: int | None = None
    experience: str | None = None
    skills: str | None = None
    education: str | None = None
    qualities: str | None = None
    interests: str | None = None

    @field_validator("experience")
    @classmethod
    def validate_experience(cls, v: str | None) -> str | None:
        """Validate the experience value"""

        char_limit: int = 10000
        if v and len(v) > char_limit:
            raise ValueError(f"Experience must not exceed {char_limit} characters")
        return v

    @field_validator("skills", "education", "qualities", "interests")
    @classmethod
    def validate_other_fields(cls, v: str | None) -> str | None:
        """Validate the field values"""

        char_limit: int = 3500
        if v and len(v) > char_limit:
            raise ValueError(f"This field must not exceed {char_limit} characters")
        return v


class UserQualificationOut(UserQualificationUpsert, OwnedOut):
    """User qualification output schema"""

    pass


# --------------------------------------------------- PASSWORD RESET ---------------------------------------------------


class PasswordResetRequest(BaseModel):
    """Email request schema for password reset"""

    email: EmailField


class PasswordReset(BaseModel):
    """Password reset schema"""

    token: str
    new_password: str


# ---------------------------------------------------- EMAIL CHANGE ----------------------------------------------------


class CheckPendingEmailResponse(BaseModel):
    """Response for checking pending email"""

    has_pending_email: bool
    pending_email: str | None = None


# -------------------------------------------------- ACCOUNT DELETION --------------------------------------------------


class AccountDeleteRequest(BaseModel):
    """Account deletion request schema"""

    password: str
