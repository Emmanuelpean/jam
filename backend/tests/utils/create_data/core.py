"""Functions for creating core test data (settings, users, AI prompts)."""

from app import models
from app.job_rating.prompts import seed_ai_prompts
from app.utilities import security
from tests.utils.create_data.utils import create_db_entries, override_properties
from tests.utils.test_data import core


def create_settings(db) -> list[models.Setting]:
    """Create sample settings"""

    data = core.SETTINGS_DATA
    print(f"Creating {len(data)} Settings...")
    return create_db_entries(db, models.Setting, data)


def create_ai_prompts(db) -> tuple[models.AiSystemPrompt, models.AiJobPromptTemplate]:
    """Create AI prompts for job rating"""

    print("Creating 2 AI prompts...")
    return seed_ai_prompts(db)


def create_users(db, user_data: list[dict] | None = None, rounds: int = 4) -> list[models.User]:
    """Create sample users with their related preferences and stripe details and return them attached to the session"""

    users = []
    original_passwords = []
    if not user_data:
        user_data = core.USER_DATA

    print(f"Creating {len(user_data)} Users...")

    # Store the original password and hash it for database storage
    for user in user_data:
        user_dict = {k: v for k, v in user.items() if k != "premium_active"}
        original_passwords.append(user_dict["password"])  # Store original password
        user_dict["password"] = security.hash_password(user_dict["password"], rounds)
        users.append(user_dict)

    users = create_db_entries(db, models.User, users)

    # Add the plain password as an attribute for test convenience
    for i, user in enumerate(users):
        user.plain_password = original_passwords[i]

    return users


def delete_user(db, user_email: str) -> None:
    """Delete a user by email and return the deleted user
    :param db: database session
    :param user_email: user email address"""

    user = db.query(models.User).filter(models.User.email == user_email).first()
    if user:
        db.delete(user)
        db.commit()


def create_user_qualifications(db, users) -> list[models.UserQualification]:
    """Create sample user qualifications"""

    data = override_properties(core.USER_QUALIFICATION_DATA, ("owner_id", users))
    print(f"Creating {len(data)} User Qualifications...")
    return create_db_entries(db, models.UserQualification, data)
