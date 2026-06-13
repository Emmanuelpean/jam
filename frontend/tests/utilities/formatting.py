"""Pure formatting helpers (mirrors of frontend utilities) used by tests and utility classes."""


def format_file_size(size: int | None) -> str:
    """Python equivalent of the frontend formatFileSize utility."""
    if not size:
        return ""
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def contiguous_subdicts(dictionary: dict) -> list[dict]:
    """Return a list of all contiguous sub-dictionaries in the given dictionary.
    :param dictionary: The dictionary to search."""

    keys = list(dictionary.keys())
    n = len(keys)
    results = []
    for size in range(1, n):
        for start in range(n):
            # Generate indices with wrap-around using modulo
            subkeys = [keys[(start + i) % n] for i in range(size)]
            subdict = {k: dictionary[k] for k in subkeys}
            results.append(subdict)
    return [dict()] + results


def format_field(label: str | None, value: str | None) -> str:
    """Format a field for display in a view modal, showing 'Not Provided' for None values.
    :param label: The field label to display
    :param value: The value to display, or None
    :return: Formatted string with label and value or 'Not Provided'"""

    if label:
        return f"{label}\n{value if value else 'Not Provided'}\n"
    else:
        return f"{value if value else 'Not Provided'}\n"
