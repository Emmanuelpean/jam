import nh3
from pydantic import EmailStr

# Tags/attributes the rich text editor (Tiptap StarterKit) can actually produce.
RICH_TEXT_ALLOWED_TAGS = {
    "p",
    "br",
    "strong",
    "b",
    "em",
    "i",
    "s",
    "del",
    "strike",
    "u",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "ul",
    "ol",
    "li",
    "blockquote",
    "code",
    "pre",
    "hr",
    "a",
}
# "rel" is deliberately excluded: nh3 auto-manages it (default link_rel="noopener noreferrer") and raises if it's
# also listed as an allowed attribute.
RICH_TEXT_ALLOWED_ATTRIBUTES = {"a": {"href", "target"}}


def clean_email(email: EmailStr | str) -> str:
    """Normalise the email address by stripping whitespace and converting to lowercase.
    :param email: The email address to be cleaned
    :return: Cleaned email address"""

    return str(email).strip().lower()


def sanitize_rich_text(value: str | None) -> str | None:
    """Sanitise rich-text HTML from the frontend editor, stripping any tag, attribute, or URL scheme
    (e.g. `<script>`, `onerror=`, `javascript:`) outside the small formatting set the editor can produce. Runs on
    every write regardless of what produced it, so a request that bypasses the frontend editor can't store an
    XSS payload in a description/note field.
    :param value: Raw field value, HTML or plain text
    :return: Sanitised value, or the original value unchanged if it isn't HTML"""

    if not value or "<" not in value:
        return value
    return nh3.clean(
        value,
        tags=RICH_TEXT_ALLOWED_TAGS,
        attributes=RICH_TEXT_ALLOWED_ATTRIBUTES,
        clean_content_tags={"script", "style"},
    )
