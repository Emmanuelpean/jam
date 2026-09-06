"""Modules for the demo users"""

from app import database
from app.config import settings
from app.utilities.strings import clean_email


def is_demo_email(email: str) -> bool:
    """Check whether an address is the one the "Try JAM" button logs in with. No user row backs it:
    the login route recognises the address and creates a throwaway user in the demo schema.
    :param email: The address to check
    :return: True if the address is the demo one"""

    return clean_email(email) == clean_email(settings.demo_user_email)


def is_demo_session() -> bool:
    """Check whether the request is authenticated as a demo user. Demo accounts exist only in the
    demo schema, which the JWT demo claim selects, so the claim is what makes a user a demo user.
    :return: True if the request carries a demo token"""

    return database.demo_mode.get(False)
