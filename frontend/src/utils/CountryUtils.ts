import type { SelectOption } from "./Utils";

export type Country = {
	name: string;
	cca2: string;
	cca3: string;
	cioc: string;
	capital: string;
	region: string;
	subregion: string;
	demonym: string;
	area: number;
};

let countriesCache: SelectOption[] | null = null;
let countriesCachePromise: Promise<SelectOption[]> | null = null;
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

const fetchCountries = async (): Promise<SelectOption[]> => {
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

			type APIResponse = {
				name: { common: string };
				cca2: string;
			}[];

			const data: APIResponse = await response.json();

			// Transform the data to match our format
			const countries: SelectOption[] = data
				.map((country) => ({
					value: country.cca2, // Use 2-letter country code
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
			return getFallbackCountries();
		}
	})();

	return countriesCachePromise;
};

export { fetchCountries };
