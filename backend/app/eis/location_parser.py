"""Location Parser Module

Extracts and parses location components from job posting location strings.
Handles postcodes, cities, countries, and remote work indicators across
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

        # Common remote work indicators
        self.remote_indicators = {"remote", "work from home", "wfh", "hybrid", "anywhere", "global"}

    def extract_postcode(self, location_str: str) -> str | None:
        """Extract postcode from location string"""
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

    def extract_country(self, location_str: str) -> str | None:
        """Extract country from location string"""
        country, _ = self.extract_country_with_match(location_str)
        return country

    def is_remote_location(self, location_str: str) -> bool:
        """Check if location indicates remote work"""
        location_lower = location_str.lower()
        return any(indicator in location_lower for indicator in self.remote_indicators)

    def extract_country_with_match(self, location_str: str) -> tuple[str | None, str | None]:
        """
        Extract country from location string and return both the standardized name and the matched text

        Returns:
            Tuple of (standardized_country_name, matched_text)
        """
        location_lower = location_str.lower().strip()

        # Sort countries by length (descending) to match longer names first
        sorted_countries = sorted(self.countries, key=len, reverse=True)

        # Direct country match using word boundaries
        for country in sorted_countries:
            pattern = r"\b" + re.escape(country) + r"\b"
            if re.search(pattern, location_lower):
                # Return standardized country name and the matched variant
                if country in ["uk", "united kingdom", "britain", "great britain"]:
                    return "United Kingdom", country
                elif country in ["usa", "united states", "united states of america", "america", "us"]:
                    return "United States", country
                elif country in ["england", "scotland", "wales", "northern ireland"]:
                    return "United Kingdom", country
                else:
                    return country.title(), country

        return None, None

    def parse_location(self, location_str: str) -> LocationCreate:
        """
        Parse a location string and extract country, city, postcode, and remote status

        Args:
            location_str: Raw location string from job posting

        Returns:
            Location schema object with parsed components
        """
        if not location_str or not location_str.strip():
            return LocationCreate()

        original_location = location_str.strip()
        location_str = original_location

        # Check if it's a remote position
        is_remote = self.is_remote_location(location_str)

        if is_remote:
            # For remote positions, still try to extract country (e.g., "Remote from the UK")
            country, _ = self.extract_country_with_match(location_str)
            return LocationCreate(country=country, city=None, postcode=None, remote=True)

        # Extract postcode first (as it's most specific)
        postcode = self.extract_postcode(location_str)
        if postcode:
            # Remove postcode from string for further processing
            location_str = re.sub(re.escape(postcode), "", location_str, flags=re.IGNORECASE).strip()

        # Extract country and handle the matched country text
        country, matched_country = self.extract_country_with_match(location_str)
        if country and matched_country:
            # For UK subdivisions, we want to keep them as potential regions
            uk_subdivisions = ["england", "scotland", "wales", "northern ireland"]

            if matched_country.lower() not in uk_subdivisions:
                # Remove non-UK subdivision countries from the string
                pattern = r"\b" + re.escape(matched_country) + r"\b"
                location_str = re.sub(pattern, "", location_str, flags=re.IGNORECASE).strip()

                # If the entire string was just the country name, we're done
                if not location_str:
                    return LocationCreate(country=country, city=None, postcode=postcode, remote=False)

        # Clean up remaining string (remove common separators)
        location_str = re.sub(r"[,;|\-]+", ",", location_str).strip(" ,")

        # Split remaining parts by comma
        parts = [part.strip() for part in location_str.split(",") if part.strip()]

        # Assign remaining parts as city (we'll ignore region since it's not in the schema)
        city = None
        if len(parts) >= 1 and parts[0]:
            city = parts[0].title()

        return LocationCreate(country=country, city=city, postcode=postcode, remote=is_remote)
