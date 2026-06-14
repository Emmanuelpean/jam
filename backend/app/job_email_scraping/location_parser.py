"""Location Parser Module

Extracts attendance type from job posting location strings and returns
a cleaned location string with attendance indicators removed."""

import re

# Attendance type indicators
_ATTENDANCE_INDICATORS = {
    "remote": ["remote", "work from home", "wfh", "anywhere", "global", "fully remote"],
    "hybrid": ["hybrid", "flexible"],
    "on-site": ["on-site", "office", "in-person", "on site", "onsite"],
}


def extract_attendance_type(location_str: str) -> str | None:
    """Extract attendance type from the location string
    :param location_str: Raw location string from the job posting
    :return: Attendance type ("remote", "hybrid", "on-site") if found, else None"""

    location_lower = location_str.lower()

    # Check if both remote and office/on-site indicators are present -> hybrid
    has_remote = any(indicator in location_lower for indicator in _ATTENDANCE_INDICATORS["remote"])
    has_office = any(indicator in location_lower for indicator in _ATTENDANCE_INDICATORS["on-site"])

    if has_remote and has_office:
        return "hybrid"

    # Check for explicit hybrid indicators
    for indicator in _ATTENDANCE_INDICATORS["hybrid"]:
        if indicator in location_lower:
            return "hybrid"

    # Check remote indicators
    if has_remote:
        return "remote"

    # Check on-site indicators
    if has_office:
        return "on-site"

    return None


def remove_attendance_indicators(location_str: str) -> str:
    """Remove attendance type indicators from location string
    :param location_str: Raw location string
    :return: Cleaned location string with attendance indicators removed"""

    cleaned = location_str

    # Collect all indicators to remove
    all_indicators = []
    for indicators in _ATTENDANCE_INDICATORS.values():
        all_indicators.extend(indicators)

    # Sort by length (longest first) to avoid partial matches
    all_indicators.sort(key=len, reverse=True)

    # Remove each indicator (case-insensitive)
    for indicator in all_indicators:
        pattern = re.compile(re.escape(indicator), re.IGNORECASE)
        cleaned = pattern.sub("", cleaned)

    # Remove common conjunctions/connectors used between attendance types
    connectors = [r"\bor\b", r"\band\b", r"\bor/and\b", r"\b&\b"]
    for connector in connectors:
        cleaned = re.sub(connector, "", cleaned, flags=re.IGNORECASE)

    # Remove empty parentheses, brackets, and braces
    cleaned = re.sub(r"\(\s*\)", "", cleaned)  # Empty ()
    cleaned = re.sub(r"\[\s*]", "", cleaned)  # Empty []
    cleaned = re.sub(r"\{\s*}", "", cleaned)  # Empty {}

    # Clean up extra whitespace, commas, and separators
    cleaned = re.sub(r"\s*[,/|•·-]\s*", ", ", cleaned)  # Normalize separators
    cleaned = re.sub(r"\s+", " ", cleaned)  # Multiple spaces to single
    cleaned = re.sub(r"^[,\s]+|[,\s]+$", "", cleaned)  # Trim leading/trailing
    cleaned = re.sub(r",+", ",", cleaned)  # Multiple commas to single
    cleaned = re.sub(r",\s*,", ",", cleaned)  # Remove duplicate commas with spaces

    # If the result is only wrapped in parentheses/brackets, unwrap it
    cleaned = re.sub(r"^\(\s*(.*?)\s*\)$", r"\1", cleaned)  # (content) -> content
    cleaned = re.sub(r"^\[\s*(.*?)\s*]$", r"\1", cleaned)  # [content] -> content
    cleaned = re.sub(r"^\{\s*(.*?)\s*}$", r"\1", cleaned)  # {content} -> content

    return cleaned.strip()


def parse_location(location_str: str) -> tuple[str, str | None]:
    """Parse a location string and extract the cleaned location and attendance type
    :param location_str: Raw location string from the job posting
    :return: Tuple of (cleaned location string, attendance_type string or None)"""

    if not location_str:
        return "", None

    location_str = location_str.strip()

    if not location_str:
        return "", None

    # Extract attendance type first
    attendance_type = extract_attendance_type(location_str)

    # Remove attendance indicators from location string
    cleaned_location = remove_attendance_indicators(location_str)

    return cleaned_location, attendance_type