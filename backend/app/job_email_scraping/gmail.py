import re


def extract_forwarding_confirmation_link(email_text: str) -> str | None:
    """Extract the Gmail forwarding confirmation (approval) link from an email body.
    The function is language-independent and relies only on Gmail's stable URL pattern.
    It ignores cancellation links (uf-).
    :param email_text: Raw email body
    :return: Forwarding confirmation link or None if not found"""

    urls = re.findall(r"https?://\S+", email_text)

    for url in urls:
        if "mail-settings.google.com/mail/vf-" in url:
            return url

    return None


def extract_gmail_originator(email_text: str) -> str | None:
    """Extract the first @gmail.com address from a Gmail forwarding confirmation email.
    :param email_text: Raw email body
    :return: Gmail originator email address or None if not found"""

    gmail_regex = r"\b[a-zA-Z0-9._%+-]+@gmail\.com\b"
    match = re.search(gmail_regex, email_text)
    return match.group(0) if match else None
