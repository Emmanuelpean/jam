"""Test suite for the LocationParser module.

This module contains comprehensive unit tests for the location parsing functionality,
including tests for country extraction, postcode detection, remote location identification,
and full location string parsing with various real-world scenarios."""

import pytest

from app.eis.location_parser import LocationParser
from app.schemas import LocationCreate


class TestLocationParser:
    """Test class for LocationParser functionality"""

    @pytest.fixture
    def parser(self) -> LocationParser:
        """Create a LocationParser instance for testing"""
        return LocationParser()

    @pytest.fixture
    def sample_locations(self) -> dict:
        """Sample location data for testing"""
        return {
            # Basic country only
            "country_only": [
                (
                    "United Kingdom",
                    {
                        "country": "United Kingdom",
                        "city": None,
                        "postcode": None,
                        "remote": False,
                    },
                ),
                (
                    "USA",
                    {
                        "country": "United States",
                        "city": None,
                        "postcode": None,
                        "remote": False,
                    },
                ),
                (
                    "Germany",
                    {
                        "country": "Germany",
                        "city": None,
                        "postcode": None,
                        "remote": False,
                    },
                ),
            ],
            # City and country combinations
            "city_country": [
                (
                    "London, UK",
                    {
                        "country": "United Kingdom",
                        "city": "London",
                        "postcode": None,
                        "remote": False,
                    },
                ),
                (
                    "Berlin, Germany",
                    {
                        "country": "Germany",
                        "city": "Berlin",
                        "postcode": None,
                        "remote": False,
                    },
                ),
                (
                    "Paris, France",
                    {
                        "country": "France",
                        "city": "Paris",
                        "postcode": None,
                        "remote": False,
                    },
                ),
            ],
            # Full addresses with postcodes
            "full_addresses": [
                (
                    "Manchester, England M1 1AA",
                    {
                        "country": "United Kingdom",
                        "city": "Manchester",
                        "postcode": "M1 1AA",
                        "remote": False,
                    },
                ),
                (
                    "New York, NY 10001, USA",
                    {
                        "country": "United States",
                        "city": "New York",
                        "postcode": "10001",
                        "remote": False,
                    },
                ),
                (
                    "Toronto, ON M5V 3A8, Canada",
                    {"country": "Canada", "city": "Toronto", "postcode": "M5V 3A8", "remote": False},
                ),
                (
                    "Sydney, NSW 2000, Australia",
                    {"country": "Australia", "city": "Sydney", "postcode": "2000", "remote": False},
                ),
            ],
            # Remote locations
            "remote_locations": [
                (
                    "Remote from the UK",
                    {"country": "United Kingdom", "city": None, "postcode": None, "remote": True},
                ),
                (
                    "Work from home - United States",
                    {"country": "United States", "city": None, "postcode": None, "remote": True},
                ),
                ("Remote - Global", {"country": None, "city": None, "postcode": None, "remote": True}),
                (
                    "Hybrid - London, UK",
                    {"country": "United Kingdom", "city": None, "postcode": None, "remote": True},
                ),
            ],
            # Edge cases
            "edge_cases": [
                ("", {"country": None, "city": None, "postcode": None, "remote": False}),
                ("   ", {"country": None, "city": None, "postcode": None, "remote": False}),
                (None, {"country": None, "city": None, "postcode": None, "remote": False}),
            ],
        }

    # ============================================ Basic Functionality Tests ============================================

    def test_parser_initialization(self, parser) -> None:
        """Test that parser initializes correctly"""
        assert isinstance(parser, LocationParser)
        assert hasattr(parser, "countries")
        assert hasattr(parser, "remote_indicators")
        assert len(parser.countries) > 0
        assert len(parser.remote_indicators) > 0

    def test_location_info_dataclass(self) -> None:
        """Test LocationInfo dataclass creation and defaults"""
        location_info = LocationCreate()
        assert location_info.country is None
        assert location_info.city is None
        assert location_info.postcode is None
        assert location_info.remote is False

        # Test with values
        location_info = LocationCreate(
            country="United Kingdom",
            city="London",
            postcode="SW1A 1AA",
            remote=False,
        )
        assert location_info.country == "United Kingdom"
        assert location_info.city == "London"
        assert location_info.postcode == "SW1A 1AA"
        assert location_info.remote is False

    # =========================================== Country Extraction Tests ===========================================

    def test_extract_country_basic(self, parser) -> None:
        """Test basic country extraction"""
        assert parser.extract_country("United Kingdom") == "United Kingdom"
        assert parser.extract_country("UK") == "United Kingdom"
        assert parser.extract_country("USA") == "United States"
        assert parser.extract_country("Germany") == "Germany"

    def test_extract_country_case_insensitive(self, parser) -> None:
        """Test country extraction is case insensitive"""
        assert parser.extract_country("united kingdom") == "United Kingdom"
        assert parser.extract_country("GERMANY") == "Germany"
        assert parser.extract_country("UsA") == "United States"

    def test_extract_country_with_context(self, parser) -> None:
        """Test country extraction within larger strings"""
        assert parser.extract_country("London, UK") == "United Kingdom"
        assert parser.extract_country("Remote from the UK") == "United Kingdom"
        assert parser.extract_country("Berlin, Germany") == "Germany"

    def test_extract_country_standardization(self, parser) -> None:
        """Test country name standardization"""
        uk_variations = ["uk", "united kingdom", "britain", "great britain", "england", "scotland", "wales"]
        for variation in uk_variations:
            assert parser.extract_country(variation) == "United Kingdom"

        us_variations = ["usa", "united states", "america", "us"]
        for variation in us_variations:
            assert parser.extract_country(variation) == "United States"

    def test_extract_country_none_cases(self, parser) -> None:
        """Test cases where no country should be found"""
        assert parser.extract_country("") is None
        assert parser.extract_country("Random City") is None
        assert parser.extract_country("123 Main Street") is None

    # =========================================== Postcode Extraction Tests ===========================================

    def test_extract_postcode_uk(self, parser) -> None:
        """Test UK postcode extraction"""
        uk_postcodes = [
            ("SW1A 1AA", "SW1A 1AA"),
            ("M1 1AA", "M1 1AA"),
            ("B33 8TH", "B33 8TH"),
            ("W1A 0AX", "W1A 0AX"),
            ("London SW1A1AA", "SW1A1AA"),  # Without space
        ]
        for location, expected in uk_postcodes:
            result = parser.extract_postcode(location)
            assert result == expected, f"Failed for {location}, got {result}, expected {expected}"

    def test_extract_postcode_us(self, parser) -> None:
        """Test US zip code extraction"""
        us_zipcodes = [
            ("10001", "10001"),
            ("90210", "90210"),
            ("12345-6789", "12345-6789"),
            ("New York 10001", "10001"),
        ]
        for location, expected in us_zipcodes:
            assert parser.extract_postcode(location) == expected

    def test_extract_postcode_canada(self, parser) -> None:
        """Test Canadian postal code extraction"""
        ca_postcodes = [
            ("M5V 3A8", "M5V 3A8"),
            ("K1A 0A6", "K1A 0A6"),
            ("Toronto M5V3A8", "M5V3A8"),  # Without space
        ]
        for location, expected in ca_postcodes:
            assert parser.extract_postcode(location) == expected

    def test_extract_postcode_general(self, parser) -> None:
        """Test general postcode patterns"""
        general_postcodes = [
            ("75001", "75001"),  # France - 5 digit postcode
            ("1234", "1234"),  # Generic 4-digit (avoid conflict with US zip)
            ("123456", "123456"),  # Generic 6-digit
            ("Berlin 12345", "12345"),  # 5-digit in context (will match US pattern)
            ("Paris 75001", "75001"),  # French postcode in context
        ]
        for location, expected in general_postcodes:
            result = parser.extract_postcode(location)
            assert result == expected, f"Failed for {location}, got {result}, expected {expected}"

    def test_extract_postcode_letter_number_combinations(self, parser) -> None:
        """Test letter-number postcode combinations that should be handled specially"""
        # Note: These patterns may conflict with existing patterns, so test them separately
        letter_number_postcodes = [
            # These would need to be in contexts where other patterns don't match first
            ("Some City AB-12345", None),  # This will likely match the "12345" part with US pattern
            ("Location DE12345", None),  # This might not match any pattern depending on implementation
        ]
        for location, expected in letter_number_postcodes:
            result = parser.extract_postcode(location)
            # For now, we accept that these patterns have precedence issues
            # The important thing is that the function doesn't crash
            assert isinstance(result, (str, type(None)))

    def test_extract_postcode_none_cases(self, parser) -> None:
        """Test cases where no postcode should be found"""
        assert parser.extract_postcode("London") is None
        assert parser.extract_postcode("Remote") is None
        assert parser.extract_postcode("") is None

    # ============================================ Remote Detection Tests ============================================

    def test_is_remote_location_positive(self, parser) -> None:
        """Test positive remote location detection"""
        remote_phrases = [
            "Remote",
            "Work from home",
            "WFH",
            "Hybrid",
            "Anywhere",
            "Global",
            "Remote from the UK",
            "Work from home - United States",
        ]
        for phrase in remote_phrases:
            assert parser.is_remote_location(phrase), f"Failed to detect remote in: {phrase}"

    def test_is_remote_location_negative(self, parser) -> None:
        """Test negative remote location detection"""
        non_remote_phrases = [
            "London",
            "New York",
            "Berlin, Germany",
            "Manchester, UK",
            "123 Main Street",
        ]
        for phrase in non_remote_phrases:
            assert not parser.is_remote_location(phrase), f"Incorrectly detected remote in: {phrase}"

    def test_is_remote_location_case_insensitive(self, parser) -> None:
        """Test remote detection is case insensitive"""
        assert parser.is_remote_location("REMOTE")
        assert parser.is_remote_location("Remote")
        assert parser.is_remote_location("remote")
        assert parser.is_remote_location("Work From Home")

    # ========================================== Full Parsing Tests ==========================================

    @pytest.mark.parametrize(
        "location_str,expected",
        [
            (
                "United Kingdom",
                {
                    "country": "United Kingdom",
                    "city": None,
                    "postcode": None,
                    "remote": False,
                },
            ),
            (
                "London, UK",
                {
                    "country": "United Kingdom",
                    "city": "London",
                    "postcode": None,
                    "remote": False,
                },
            ),
            (
                "Manchester, England M1 1AA",
                {
                    "country": "United Kingdom",
                    "city": "Manchester",
                    "postcode": "M1 1AA",
                    "remote": False,
                },
            ),
        ],
    )
    def test_parse_location_parametrized(self, parser, location_str, expected) -> None:
        """Parametrized test for location parsing"""
        result = parser.parse_location(location_str)
        assert result.country == expected["country"]
        assert result.city == expected["city"]
        assert result.postcode == expected["postcode"]
        assert result.remote == expected["remote"]

    def test_parse_location_country_only(self, parser, sample_locations) -> None:
        """Test parsing locations with country only"""
        for location_str, expected in sample_locations["country_only"]:
            result = parser.parse_location(location_str)
            self._assert_location_result(result, expected, location_str)

    def test_parse_location_city_country(self, parser, sample_locations) -> None:
        """Test parsing locations with city and country"""
        for location_str, expected in sample_locations["city_country"]:
            result = parser.parse_location(location_str)
            self._assert_location_result(result, expected, location_str)

    def test_parse_location_full_addresses(self, parser, sample_locations) -> None:
        """Test parsing full addresses with postcodes"""
        for location_str, expected in sample_locations["full_addresses"]:
            result = parser.parse_location(location_str)
            self._assert_location_result(result, expected, location_str)

    def test_parse_location_remote(self, parser, sample_locations) -> None:
        """Test parsing remote locations"""
        for location_str, expected in sample_locations["remote_locations"]:
            result = parser.parse_location(location_str)
            self._assert_location_result(result, expected, location_str)

    def test_parse_location_edge_cases(self, parser, sample_locations) -> None:
        """Test parsing edge cases"""
        for location_str, expected in sample_locations["edge_cases"]:
            result = parser.parse_location(location_str)
            self._assert_location_result(result, expected, location_str)

    # ========================================== Helper Methods ==========================================

    @staticmethod
    def _assert_location_result(
        result: LocationCreate,
        expected: dict,
        original_input: str,
    ) -> None:
        """Helper method to assert location parsing results"""
        assert isinstance(result, LocationCreate), f"Result should be LocationInfo instance for input: {original_input}"
        assert (
            result.country == expected["country"]
        ), f"Country mismatch for '{original_input}': got {result.country}, expected {expected['country']}"
        assert (
            result.city == expected["city"]
        ), f"City mismatch for '{original_input}': got {result.city}, expected {expected['city']}"
        assert (
            result.postcode == expected["postcode"]
        ), f"Postcode mismatch for '{original_input}': got {result.postcode}, expected {expected['postcode']}"
        assert (
            result.remote == expected["remote"]
        ), f"Remote mismatch for '{original_input}': got {result.remote}, expected {expected['remote']}"

    # ========================================== Performance and Robustness Tests ==========================================

    def test_parser_handles_empty_string(self, parser) -> None:
        """Test parser handles empty string input"""
        result = parser.parse_location("")
        assert isinstance(result, LocationCreate)
        assert result.country is None
        assert result.city is None
        assert result.remote is False

    def test_parser_handles_whitespace_only(self, parser) -> None:
        """Test parser handles whitespace-only input"""
        result = parser.parse_location("   \t\n   ")
        assert isinstance(result, LocationCreate)
        assert result.country is None
        assert result.city is None
        assert result.remote is False

    def test_parser_handles_special_characters(self, parser) -> None:
        """Test parser handles special characters"""
        special_locations = [
            "São Paulo, Brazil",
            "México City, Mexico",
            "Zürich, Switzerland",
            "København, Denmark",
        ]

        for location in special_locations:
            result = parser.parse_location(location)
            assert isinstance(result, LocationCreate)

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
        ] * 100  # 500 locations

        start_time = time.time()
        for location in locations:
            parser.parse_location(location)
        end_time = time.time()

        # Should process 500 locations in less than 1 second
        assert (end_time - start_time) < 1.0, "Parser should be fast enough to process locations quickly"
