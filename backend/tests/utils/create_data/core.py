"""Functions for creating core test data (settings, users, AI prompts)."""

from app import models, utils
from app.job_rating.prompts import seed_ai_prompts
from tests.utils.test_data import basics
from tests.utils.create_data.utils import add_to_db, override_entries_properties, add_to_db2


def create_settings(db) -> list[models.Setting]:
    """Create sample settings"""

    print("Creating settings...")
    return add_to_db2(db, models.Setting, basics.SETTINGS_DATA)


def create_ai_prompts(db) -> tuple[models.AiSystemPrompt, models.AiJobPromptTemplate]:
    """Create AI prompts for job rating"""

    print("Creating AI prompts...")
    return seed_ai_prompts(db)


def create_users(db, user_data: list[dict] | None = None, rounds=4) -> list[models.User]:
    """Create sample users with their related preferences and stripe details, and return them attached to the session"""

    print("Creating users...")
    users = []
    original_passwords = []
    if not user_data:
        user_data = basics.USER_DATA

    # Store the original password and hash it for database storage
    for user in user_data:
        user_dict = {k: v for k, v in user.items() if k != "premium_active"}
        original_passwords.append(user_dict["password"])  # Store original password
        user_dict["password"] = utils.hash_password(user_dict["password"], rounds)

        # Create user
        # noinspection PyArgumentList
        new_user = models.User(**user_dict)
        users.append(new_user)

    users = add_to_db(db, users)

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

    print("Creating user qualifications...")
    # noinspection PyArgumentList
    keywords = [
        models.UserQualification(**kwargs)
        for kwargs in override_entries_properties(basics.USER_QUALIFICATION_DATA, ("owner_id", users))
    ]
    return add_to_db(db, keywords)
