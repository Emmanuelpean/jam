// Cache for countries to avoid repeated API calls
let countriesCache = null;
let countriesCachePromise = null;

export const fetchCountries = async () => {
	// Return cached data if available
	if (countriesCache) {
		return countriesCache;
	}

	// Return existing promise if already fetching
	if (countriesCachePromise) {
		return countriesCachePromise;
	}

	// Create new fetch promise
	countriesCachePromise = (async () => {
		try {
			const response = await fetch("https://restcountries.com/v3.1/all?fields=name,cca2");

			if (!response.ok) {
				throw new Error("Failed to fetch countries");
			}

			const data = await response.json();

			// Transform the data to match our format
			const countries = data
				.map((country) => ({
					value: country.name.common, // 2-letter country code
					label: country.name.common, // Common country name
				}))
				.sort((a, b) => a.label.localeCompare(b.label)); // Sort alphabetically

			// Cache the result
			countriesCache = countries;
			countriesCachePromise = null;

			return countries;
		} catch (error) {
			console.error("Error fetching countries:", error);
			countriesCachePromise = null;

			// Fallback to a basic list if API fails
			return getFallbackCountries();
		}
	})();

	return countriesCachePromise;
};

// Fallback list of major countries in case API fails
const getFallbackCountries = () => [
	{ value: "US", label: "United States" },
	{ value: "GB", label: "United Kingdom" },
	{ value: "CA", label: "Canada" },
	{ value: "AU", label: "Australia" },
	{ value: "DE", label: "Germany" },
	{ value: "FR", label: "France" },
	{ value: "IT", label: "Italy" },
	{ value: "ES", label: "Spain" },
	{ value: "NL", label: "Netherlands" },
	{ value: "SE", label: "Sweden" },
	{ value: "NO", label: "Norway" },
	{ value: "DK", label: "Denmark" },
	{ value: "FI", label: "Finland" },
	{ value: "CH", label: "Switzerland" },
	{ value: "AT", label: "Austria" },
	{ value: "BE", label: "Belgium" },
	{ value: "IE", label: "Ireland" },
	{ value: "PT", label: "Portugal" },
	{ value: "GR", label: "Greece" },
	{ value: "PL", label: "Poland" },
	{ value: "CZ", label: "Czech Republic" },
	{ value: "HU", label: "Hungary" },
	{ value: "SK", label: "Slovakia" },
	{ value: "SI", label: "Slovenia" },
	{ value: "HR", label: "Croatia" },
	{ value: "RO", label: "Romania" },
	{ value: "BG", label: "Bulgaria" },
	{ value: "LT", label: "Lithuania" },
	{ value: "LV", label: "Latvia" },
	{ value: "EE", label: "Estonia" },
	{ value: "MT", label: "Malta" },
	{ value: "CY", label: "Cyprus" },
	{ value: "LU", label: "Luxembourg" },
	{ value: "JP", label: "Japan" },
	{ value: "KR", label: "South Korea" },
	{ value: "CN", label: "China" },
	{ value: "IN", label: "India" },
	{ value: "SG", label: "Singapore" },
	{ value: "HK", label: "Hong Kong" },
	{ value: "NZ", label: "New Zealand" },
	{ value: "BR", label: "Brazil" },
	{ value: "MX", label: "Mexico" },
	{ value: "AR", label: "Argentina" },
	{ value: "ZA", label: "South Africa" },
];
