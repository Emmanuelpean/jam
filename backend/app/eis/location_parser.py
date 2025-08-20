"""Location Parser Module

Extracts and parses location components from job posting location strings.
Handles postcodes, cities, countries, and attendance type indicators across
multiple international formats including UK, US, and Canadian postal codes."""

import re

from app.schemas import LocationCreate


class LocationParser:
    """Parser for extracting location components from job location strings"""

    def __init__(self) -> None:

        # Common country names and variations
        self.countries = {
            "uk",
            "united kingdom",
            "britain",
            "great britain",
            "england",
            "scotland",
            "wales",
            "northern ireland",
            "usa",
            "united states",
            "united states of america",
            "america",
            "us",
            "canada",
            "australia",
            "germany",
            "france",
            "italy",
            "spain",
            "netherlands",
            "belgium",
            "ireland",
            "switzerland",
            "austria",
            "sweden",
            "norway",
            "denmark",
            "finland",
            "poland",
            "czech republic",
            "hungary",
            "portugal",
            "greece",
            "turkey",
            "india",
            "china",
            "japan",
            "singapore",
            "hong kong",
            "south korea",
            "brazil",
            "mexico",
            "argentina",
            "chile",
            "colombia",
        }

        # UK postcode pattern
        self.uk_postcode_pattern = r"\b[A-Z]{1,2}[0-9][A-Z0-9]?\s?[0-9][A-Z]{2}\b"

        # US zip code pattern
        self.us_zipcode_pattern = r"\b\d{5}(?:-\d{4})?\b"

        # Canadian postal code pattern
        self.ca_postcode_pattern = r"\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b"

        # General postcode patterns for other countries
        self.general_postcode_patterns = [
            r"\b\d{4,6}\b",  # 4-6 digit postcodes
            r"\b[A-Z]{2}-?\d{3,5}\b",  # Letter-number combinations
        ]

        # Attendance type indicators
        self.attendance_indicators = {
            "remote": ["remote", "work from home", "wfh", "anywhere", "global", "fully remote"],
            "hybrid": ["hybrid", "flexible"],
            "on-site": ["on-site", "office", "in-person", "on site", "onsite"],
        }

    def extract_postcode(self, location_str: str) -> str | None:
        """Extract postcode from the location string
        :param location_str: Raw location string from the job posting
        :return: Postcode string if found, else None"""

        location_upper = location_str.upper()

        # Try UK postcode first
        uk_match = re.search(self.uk_postcode_pattern, location_upper)
        if uk_match:
            return uk_match.group().strip()

        # Try US zip code
        us_match = re.search(self.us_zipcode_pattern, location_str)
        if us_match:
            return us_match.group().strip()

        # Try Canadian postal code
        ca_match = re.search(self.ca_postcode_pattern, location_upper)
        if ca_match:
            return ca_match.group().strip()

        # Try general patterns
        for pattern in self.general_postcode_patterns:
            match = re.search(pattern, location_upper)
            if match:
                return match.group().strip()

        return None

    def extract_attendance_type(self, location_str: str) -> str | None:
        """Extract attendance type from the location string
        :param location_str: Raw location string from the job posting
        :return: Attendance type ("remote", "hybrid", "on-site") if found, else None"""

        location_lower = location_str.lower()

        # Check if both remote and office/on-site indicators are present -> hybrid
        has_remote = any(indicator in location_lower for indicator in self.attendance_indicators["remote"])
        has_office = any(indicator in location_lower for indicator in self.attendance_indicators["on-site"])

        if has_remote and has_office:
            return "hybrid"

        # Check for explicit hybrid indicators
        for indicator in self.attendance_indicators["hybrid"]:
            if indicator in location_lower:
                return "hybrid"

        # Check remote indicators
        if has_remote:
            return "remote"

        # Check on-site indicators
        if has_office:
            return "on-site"

        return None

    def extract_country_with_match(self, location_str: str) -> tuple[str | None, str | None]:
        """Extract country from the location string and return both the standardised name and the matched text
        :param location_str: Raw location string from the job posting
        :return: Standardised country name and the original name or (None, None) if not found"""

        location_lower = location_str.lower().strip()

        # Sort countries by length (descending) to match longer names first
        sorted_countries = sorted(self.countries, key=len, reverse=True)

        # Direct country match using word boundaries
        for country in sorted_countries:
            pattern = r"\b" + re.escape(country) + r"\b"
            if re.search(pattern, location_lower):
                # Return the standardised country name and the matched variant
                if country in [
                    "uk",
                    "united kingdom",
                    "britain",
                    "great britain",
                    "england",
                    "scotland",
                    "wales",
                    "northern ireland",
                ]:
                    return "United Kingdom", country
                elif country in ["usa", "united states", "united states of america", "america", "us"]:
                    return "United States", country
                else:
                    return country.title(), country

        return None, None

    def parse_location(self, location_str: str) -> tuple[LocationCreate, str | None]:
        """Parse a location string and extract country, city, postcode, and attendance type
        :param location_str: Raw location string from the job posting
        :return: Tuple of (LocationCreate object, attendance_type string or None)"""

        location_str = location_str.strip()

        if not location_str:
            return LocationCreate(), None

        # Extract attendance type first
        attendance_type = self.extract_attendance_type(location_str)

        # Create a working copy of the string for location parsing
        working_str = location_str

        # Remove attendance type indicators from the working string for cleaner location parsing
        if attendance_type:
            for indicator_list in self.attendance_indicators.values():
                for indicator in indicator_list:
                    # Remove the indicator and clean up whitespace/punctuation
                    pattern = r"\b" + re.escape(indicator) + r"\b"
                    working_str = re.sub(pattern, "", working_str, flags=re.IGNORECASE)

        # Clean up the working string
        working_str = re.sub(r"\s*[-,;|]\s*", " ", working_str).strip()
        working_str = re.sub(r"\s+", " ", working_str)  # Normalize whitespace

        # If the string is now empty or just punctuation, we only have attendance type info
        if not working_str or re.match(r"^\W*$", working_str):
            return LocationCreate(), attendance_type

        # Extract postcode first (as it's most specific)
        postcode = self.extract_postcode(working_str)
        if postcode:
            working_str = re.sub(re.escape(postcode), "", working_str, flags=re.IGNORECASE).strip()

        # Extract country and handle the matched country text
        country, original = self.extract_country_with_match(working_str)
        if country and original:
            pattern = r"\b" + re.escape(original) + r"\b"
            working_str = re.sub(pattern, "", working_str, flags=re.IGNORECASE).strip()

        # Clean up the remaining string (remove common separators)
        working_str = re.sub(r"[,;|\-]+", ",", working_str).strip(" ,")

        # Remove common prepositions and articles that shouldn't be city names
        prepositions_and_articles = [
            "from",
            "in",
            "at",
            "to",
            "for",
            "with",
            "by",
            "of",
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
        ]

        for word in prepositions_and_articles:
            pattern = r"\b" + re.escape(word) + r"\b"
            working_str = re.sub(pattern, "", working_str, flags=re.IGNORECASE)

        # Clean up whitespace and separators again after removing prepositions
        working_str = re.sub(r"\s*[-,;|]\s*", ",", working_str).strip(" ,")
        working_str = re.sub(r"\s+", " ", working_str).strip()

        # Split remaining parts by comma
        parts = [part.strip() for part in working_str.split(",") if part.strip()]

        # Assign remaining parts as city
        city = None
        if len(parts) >= 1 and parts[0]:
            city = parts[0].title()

        location = LocationCreate(country=country, city=city, postcode=postcode)
        return location, attendance_type

    def parse_location_only(self, location_str: str) -> LocationCreate:
        """Parse a location string and return only the location data (for backward compatibility)
        :param location_str: Raw location string from the job posting
        :return: Location schema object with parsed components"""

        location, _ = self.parse_location(location_str)
        return location
