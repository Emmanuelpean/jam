"""Test suite for the LocationParser module.

This module contains comprehensive unit tests for the location parsing functionality,
focusing on attendance type extraction and preserving the raw location string."""

import pytest

from app.job_email_scraping.location_parser import extract_attendance_type, parse_location


@pytest.mark.parametrize(
    "location_str,expected",
    [
        ("Remote", "remote"),
        ("Work from home", "remote"),
        ("WFH", "remote"),
        ("Fully remote", "remote"),
        ("Anywhere", "remote"),
        ("Global", "remote"),
        ("Remote from the UK", "remote"),
        ("Work from home - United States", "remote"),
    ],
)
def test_extract_attendance_type_remote(location_str: str, expected: str) -> None:
    """Test remote attendance type extraction"""

    result = extract_attendance_type(location_str)
    assert result == expected, f"Failed for {location_str}, got {result}, expected {expected}"


@pytest.mark.parametrize(
    "location_str,expected",
    [
        ("Hybrid", "hybrid"),
        ("Flexible", "hybrid"),
        ("Mix of office and remote", "hybrid"),
        ("Office/remote", "hybrid"),
        ("Hybrid - London, UK", "hybrid"),
    ],
)
def test_extract_attendance_type_hybrid(location_str: str, expected: str) -> None:
    """Test hybrid attendance type extraction"""

    result = extract_attendance_type(location_str)
    assert result == expected, f"Failed for {location_str}, got {result}, expected {expected}"


@pytest.mark.parametrize(
    "location_str,expected",
    [
        ("On-site", "on-site"),
        ("Office", "on-site"),
        ("In-person", "on-site"),
        ("On site", "on-site"),
        ("Onsite", "on-site"),
    ],
)
def test_extract_attendance_type_onsite(location_str: str, expected: str) -> None:
    """Test on-site attendance type extraction"""

    result = extract_attendance_type(location_str)
    assert result == expected, f"Failed for {location_str}, got {result}, expected {expected}"


@pytest.mark.parametrize(
    "location_str,expected",
    [
        ("London", None),
        ("New York", None),
        ("Berlin, Germany", None),
        ("Manchester, UK", None),
        ("123 Main Street", None),
    ],
)
def test_extract_attendance_type_none_cases(location_str: str, expected: str) -> None:
    """Test cases where no attendance type should be found"""

    result = extract_attendance_type(location_str)
    assert result == expected


@pytest.mark.parametrize(
    "location_str,expected",
    [
        ("REMOTE", "remote"),
        ("Remote", "remote"),
        ("remote", "remote"),
        ("Work From Home", "remote"),
        ("HYBRID", "hybrid"),
        ("ON-SITE", "on-site"),
    ],
)
def test_extract_attendance_type_case_insensitive(location_str: str, expected: str) -> None:
    """Test attendance type detection is case-insensitive"""

    assert extract_attendance_type(location_str) == expected


@pytest.mark.parametrize(
    "location_str,expected_location,expected_attendance",
    [
        ("United Kingdom", "United Kingdom", None),
        ("USA", "USA", None),
        ("Germany", "Germany", None),
        ("London, UK", "London, UK", None),
        ("Berlin, Germany", "Berlin, Germany", None),
        ("Paris, France", "Paris, France", None),
        ("Manchester, England M1 1AA", "Manchester, England M1 1AA", None),
        ("Sydney, 2000, Australia", "Sydney, 2000, Australia", None),
        ("Remote from the UK", "from the UK", "remote"),
        ("Work from home - United States", "United States", "remote"),
        ("Oxford (Remote)", "Oxford", "remote"),
        ("Oxford [Remote]", "Oxford", "remote"),
        ("Oxford {Remote}", "Oxford", "remote"),
        ("Remote (United States)", "United States", "remote"),
        ("Remote - Global", "", "remote"),
        ("Hybrid - London, UK", "London, UK", "hybrid"),
        ("On-site - Berlin, Germany", "Berlin, Germany", "on-site"),
        ("Remote", "", "remote"),
        ("Hybrid", "", "hybrid"),
        ("", "", None),
        ("   ", "", None),
        ("  \t\n ", "", None),
    ],
)
def test_parse_location_parametrized(
    location_str: str, expected_location: str, expected_attendance: str | None
) -> None:
    """Test parsing locations returns raw string and attendance type"""
    location, attendance_type = parse_location(location_str)

    assert (
        location == expected_location
    ), f"Location mismatch for '{location_str}': got '{location}', expected '{expected_location}'"
    assert (
        attendance_type == expected_attendance
    ), f"Attendance type mismatch for '{location_str}': got {attendance_type}, expected {expected_attendance}"


@pytest.mark.parametrize(
    "location_str",
    [
        "São Paulo, Brazil",
        "México City, Mexico",
        "Zürich, Switzerland",
        "København, Denmark",
    ],
)
def test_parser_handles_special_characters(location_str: str) -> None:
    """Test parser handles special characters"""
    location, attendance_type = parse_location(location_str)
    assert location == location_str
    assert isinstance(attendance_type, (str, type(None)))


def test_parse_location_with_mixed_attendance_indicators() -> None:
    """Test location strings with multiple attendance type indicators"""
    # Both remote and office -> hybrid
    location, attendance = parse_location("Remote or office - London, UK")
    assert location == "London, UK"
    assert attendance == "hybrid"

    # Multiple remote indicators -> still remote
    location, attendance = parse_location("Remote, WFH, work from home")
    assert location == ""
    assert attendance == "remote"


def test_parse_location_returns_tuple() -> None:
    """Test that parse_location always returns a tuple"""
    result = parse_location("London, UK")
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], (str, type(None)))
