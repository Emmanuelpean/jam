import type { SelectOption } from "./Utils";

let countriesCache: SelectOption[] | null = null;
let countriesCachePromise: Promise<SelectOption[]> | null = null;
const getFallbackCountries = (): SelectOption[] => [
	{ value: "United States", label: "United States" },
	{ value: "United Kingdom", label: "United Kingdom" },
	{ value: "Canada", label: "Canada" },
	{ value: "Australia", label: "Australia" },
	{ value: "Germany", label: "Germany" },
	{ value: "France", label: "France" },
	{ value: "Italy", label: "Italy" },
	{ value: "Spain", label: "Spain" },
	{ value: "Netherlands", label: "Netherlands" },
	{ value: "Sweden", label: "Sweden" },
	{ value: "Norway", label: "Norway" },
	{ value: "Denmark", label: "Denmark" },
	{ value: "Finland", label: "Finland" },
	{ value: "Switzerland", label: "Switzerland" },
	{ value: "Austria", label: "Austria" },
	{ value: "Belgium", label: "Belgium" },
	{ value: "Ireland", label: "Ireland" },
	{ value: "Portugal", label: "Portugal" },
	{ value: "Greece", label: "Greece" },
	{ value: "Poland", label: "Poland" },
	{ value: "Czech Republic", label: "Czech Republic" },
	{ value: "Hungary", label: "Hungary" },
	{ value: "Slovakia", label: "Slovakia" },
	{ value: "Slovenia", label: "Slovenia" },
	{ value: "Croatia", label: "Croatia" },
	{ value: "Romania", label: "Romania" },
	{ value: "Bulgaria", label: "Bulgaria" },
	{ value: "Lithuania", label: "Lithuania" },
	{ value: "Latvia", label: "Latvia" },
	{ value: "Estonia", label: "Estonia" },
	{ value: "Malta", label: "Malta" },
	{ value: "Cyprus", label: "Cyprus" },
	{ value: "Luxembourg", label: "Luxembourg" },
	{ value: "Japan", label: "Japan" },
	{ value: "South Korea", label: "South Korea" },
	{ value: "China", label: "China" },
	{ value: "India", label: "India" },
	{ value: "Singapore", label: "Singapore" },
	{ value: "Hong Kong", label: "Hong Kong" },
	{ value: "New Zealand", label: "New Zealand" },
	{ value: "Brazil", label: "Brazil" },
	{ value: "Mexico", label: "Mexico" },
	{ value: "Argentina", label: "Argentina" },
	{ value: "South Africa", label: "South Africa" },
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
					value: country.name.common, // Use 2-letter country code
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
