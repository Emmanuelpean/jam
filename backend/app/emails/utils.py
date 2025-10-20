from email.utils import parseaddr
from app import models


def clean_email_address(sender_field: str) -> str:
    """Extract a clean email address from the sender field
    Handles formats like:
    - 'John Doe <john.doe@gmail.com>'
    - 'john.doe@gmail.com'
    - '"John Doe" <john.doe@gmail.com>'"""

    name, email = parseaddr(sender_field)
    return email.lower().strip() if email else sender_field.lower().strip()


def get_user_id_from_email(email: str, db) -> None | int:
    """Get user id from email"""

    entry = db.query(models.User).filter(models.User.email == email).first()
    if entry:
        return entry.id
    else:
        raise AssertionError(f"User with email '{email}' not found in database.")
