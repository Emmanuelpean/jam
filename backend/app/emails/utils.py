"""Utility functions for email processing"""

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


def build_multi_from_query(email_addresses: str | list[str]) -> str:
    """Build a nested OR query string for multiple FROM email addresses
    :param email_addresses: A single email address or a list of email addresses
    :return: A query string for searching emails from multiple addresses"""

    if isinstance(email_addresses, str):
        email_addresses = [email_addresses]

    query = f'FROM "{email_addresses[0]}"'
    for email in email_addresses[1:]:
        query = f'OR {query} FROM "{email}"'
    return query
