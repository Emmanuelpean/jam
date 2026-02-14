"""Test suite for the LocationParser module.

This module contains comprehensive unit tests for the location parsing functionality,
focusing on attendance type extraction and preserving the raw location string."""

import pytest

from app.job_email_scraping.location_parser import LocationParser


class TestLocationParser:
    """Test class for LocationParser functionality"""

    @pytest.fixture
    def parser(self) -> LocationParser:
        """Create a LocationParser instance for testing"""
        return LocationParser()

    # ------------------------------------------ Attendance Type Extraction Tests ----------------------------------

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
    def test_extract_attendance_type_remote(self, parser, location_str, expected) -> None:
        """Test remote attendance type extraction"""
        result = parser.extract_attendance_type(location_str)
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
    def test_extract_attendance_type_hybrid(self, parser, location_str, expected) -> None:
        """Test hybrid attendance type extraction"""
        result = parser.extract_attendance_type(location_str)
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
    def test_extract_attendance_type_onsite(self, parser, location_str, expected) -> None:
        """Test on-site attendance type extraction"""
        result = parser.extract_attendance_type(location_str)
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
    def test_extract_attendance_type_none_cases(self, parser, location_str, expected) -> None:
        """Test cases where no attendance type should be found"""
        result = parser.extract_attendance_type(location_str)
        assert result == expected

    def test_extract_attendance_type_case_insensitive(self, parser) -> None:
        """Test attendance type detection is case-insensitive"""
        assert parser.extract_attendance_type("REMOTE") == "remote"
        assert parser.extract_attendance_type("Remote") == "remote"
        assert parser.extract_attendance_type("remote") == "remote"
        assert parser.extract_attendance_type("Work From Home") == "remote"
        assert parser.extract_attendance_type("HYBRID") == "hybrid"
        assert parser.extract_attendance_type("ON-SITE") == "on-site"

    # ----------------------------------------------- Full Parsing Tests -----------------------------------------------

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
        ],
    )
    def test_parse_location_parametrized(self, parser, location_str, expected_location, expected_attendance) -> None:
        """Test parsing locations returns raw string and attendance type"""
        location, attendance_type = parser.parse_location(location_str)

        assert (
            location == expected_location
        ), f"Location mismatch for '{location_str}': got '{location}', expected '{expected_location}'"
        assert (
            attendance_type == expected_attendance
        ), f"Attendance type mismatch for '{location_str}': got {attendance_type}, expected {expected_attendance}"

    # ---------------------------------------- Performance and Robustness Tests ----------------------------------------

    def test_parser_handles_empty_string(self, parser) -> None:
        """Test parser handles empty string input"""
        location, attendance_type = parser.parse_location("")
        assert location == ""
        assert attendance_type is None

    def test_parser_handles_whitespace_only(self, parser) -> None:
        """Test parser handles whitespace-only input"""
        location, attendance_type = parser.parse_location("   \t\n   ")
        assert location == ""
        assert attendance_type is None

    @pytest.mark.parametrize(
        "location_str",
        [
            "São Paulo, Brazil",
            "México City, Mexico",
            "Zürich, Switzerland",
            "København, Denmark",
        ],
    )
    def test_parser_handles_special_characters(self, parser, location_str) -> None:
        """Test parser handles special characters"""
        location, attendance_type = parser.parse_location(location_str)
        assert location == location_str
        assert isinstance(attendance_type, (str, type(None)))

    @pytest.mark.performance
    def test_parser_performance(self, parser) -> None:
        """Test parser performance with many locations"""
        import time

        locations = [
            "London, UK",
            "New York, USA",
            "Berlin, Germany",
            "Remote from anywhere",
            "Sydney, Australia",
            "Hybrid - Paris, France",
            "On-site - Tokyo, Japan",
        ] * 100  # 700 locations

        start_time = time.time()
        for location in locations:
            parser.parse_location(location)
        end_time = time.time()

        # Should process 700 locations in less than 1 second
        assert (end_time - start_time) < 1.0, "Parser should be fast enough to process locations quickly"

    # ---------------------------------------- Complex Scenarios Tests ----------------------------------------

    def test_parse_location_with_mixed_attendance_indicators(self, parser) -> None:
        """Test location strings with multiple attendance type indicators"""
        # Both remote and office -> hybrid
        location, attendance = parser.parse_location("Remote or office - London, UK")
        assert location == "London, UK"
        assert attendance == "hybrid"

        # Multiple remote indicators -> still remote
        location, attendance = parser.parse_location("Remote, WFH, work from home")
        assert location == ""
        assert attendance == "remote"

    def test_parse_location_returns_tuple(self, parser) -> None:
        """Test that parse_location always returns a tuple"""
        result = parser.parse_location("London, UK")
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)
        assert isinstance(result[1], (str, type(None)))
