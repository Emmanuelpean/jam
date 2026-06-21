from pydantic import EmailStr


def clean_email(email: EmailStr | str) -> str:
    """Normalise the email address by stripping whitespace and converting to lowercase.
    :param email: The email address to be cleaned
    :return: Cleaned email address"""

    return str(email).strip().lower()
