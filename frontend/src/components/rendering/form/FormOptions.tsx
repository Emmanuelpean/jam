import { findItemById } from "../../../utils/Utils";
import { useMemo } from "react";
import { DataContextValue, useDataContext } from "../../../contexts/DataContext";
import { SelectWidgetPreviewConfig } from "../widgets/SelectWidget";
import { modalViewFields } from "../view/ModalFields";
import { PersonData } from "../../../services/Schemas";
import stringSimilarity from "string-similarity";

export type SelectOption = {
	value: string;
	label: string;
	data?: any;
};

export function findClosestOption(options: SelectOption[], name: string): string | null {
	if (!name || options.length === 0) return null;
	const names: string[] = options.map((c: SelectOption): string => c.label);
	const result = stringSimilarity.findBestMatch(name, names);

	const MIN_SIMILARITY_THRESHOLD = 0.4;

	if (result.bestMatch.rating < MIN_SIMILARITY_THRESHOLD) {
		return null;
	}

	return options[result.bestMatchIndex]?.value || null;
}

export function findExactOption(options: SelectOption[], name: string): string | null | undefined {
	if (!name || options.length === 0) return null;
	const match: SelectOption | undefined = options.find(
		(opt: SelectOption): boolean => opt.label.toLowerCase() === name.toLowerCase(),
	);
	return match ? match.value : null;
}

interface UseFormOptionsReturn {
	companies: SelectOption[];
	locations: SelectOption[];
	keywords: SelectOption[];
	persons: SelectOption[];
	aggregators: SelectOption[];
	jobs: SelectOption[];
	countries: SelectOption[];
	currencies: SelectOption[];
	currencyNames: SelectOption[];
	getCompanyPreviewConfig: SelectWidgetPreviewConfig;
	getPersonPreviewConfig: SelectWidgetPreviewConfig;
	getLocationPreviewConfig: SelectWidgetPreviewConfig;
	getAggregatorPreviewConfig: SelectWidgetPreviewConfig;
}

export const toSelectOptions = <T extends Record<string, any>>(
	data: T[],
	valueKey: keyof T | ((item: T) => any) = "id",
	labelKey: keyof T | ((item: T) => any) = "name",
): SelectOption[] => {
	const sorted = [...data].sort((a, b) => {
		const aLabel = typeof labelKey === "function" ? labelKey(a) : a[labelKey];
		const bLabel = typeof labelKey === "function" ? labelKey(b) : b[labelKey];
		return String(aLabel).localeCompare(String(bLabel));
	});

	return sorted.map(
		(item): SelectOption => ({
			value: typeof valueKey === "function" ? valueKey(item) : item[valueKey],
			label: typeof labelKey === "function" ? labelKey(item) : item[labelKey],
			data: item,
		}),
	);
};

export const useFormOptions = (): UseFormOptionsReturn => {
	const contextData: DataContextValue = useDataContext();

	const getCompanyPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [modalViewFields.name({ isTitle: true }), modalViewFields.url(), [modalViewFields.description()]],
		getDataById: (id: number) => findItemById(contextData.companies, id),
	};

	const getPersonPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [
			modalViewFields.name({ isTitle: true }),
			modalViewFields.email(),
			[modalViewFields.companyBadge(), modalViewFields.role()],
		],
		getDataById: (id: number) => findItemById(contextData.persons, id),
	};

	const getLocationPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [modalViewFields.name({ isTitle: true }), modalViewFields.locationMap({ label: "" })],
		getDataById: (id: number) => findItemById(contextData.locations, id),
	};

	const getAggregatorPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [modalViewFields.name({ isTitle: true }), modalViewFields.url()],
		getDataById: (id: number) => findItemById(contextData.aggregators, id),
	};

	const getPersonLabel = (person: PersonData): string => {
		if (person.company_id) {
			const company = findItemById(contextData.companies, person.company_id);
			if (company) {
				return `${person.name} (${company.name})`;
			}
		}
		return person.name;
	};

	// Convert data to SelectOptions and memoize
	const companyOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.companies),
		[contextData.companies],
	);
	const locationOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.locations),
		[contextData.locations],
	);
	const keywordOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.keywords),
		[contextData.keywords],
	);
	const personOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.persons, "id", getPersonLabel),
		[contextData.persons],
	);
	const aggregatorOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.aggregators),
		[contextData.aggregators],
	);
	const jobOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.jobs, "id", "name"),
		[contextData.jobs],
	);
	const countryOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.countries, "name", "name"),
		[contextData.countries],
	);
	const currencyOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.currencies, "code", "symbol"),
		[contextData.currencies],
	);
	const currencyNameOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(contextData.currencies, "code", "name"),
		[contextData.currencies],
	);

	return {
		companies: companyOptions,
		locations: locationOptions,
		keywords: keywordOptions,
		persons: personOptions,
		aggregators: aggregatorOptions,
		jobs: jobOptions,
		countries: countryOptions,
		currencies: currencyOptions,
		currencyNames: currencyNameOptions,
		getCompanyPreviewConfig,
		getPersonPreviewConfig,
		getLocationPreviewConfig,
		getAggregatorPreviewConfig,
	};
};

export const appliedViaOptions: SelectOption[] = [
	{ value: "aggregator", label: "Aggregator" },
	{ value: "company_website", label: "Company Website" },
	{ value: "email", label: "Email" },
	{ value: "phone", label: "Phone" },
	{ value: "other", label: "Other" },
];

export const applicationStatusOptions: SelectOption[] = [
	{ value: "applied", label: "Applied" },
	{ value: "interview", label: "Interview" },
	{ value: "rejected", label: "Rejected" },
	{ value: "offer", label: "Offer" },
	{ value: "withdrawn", label: "Withdrawn" },
];

export const attendanceTypeOptions: SelectOption[] = [
	{ value: "on-site", label: "On-site" },
	{ value: "hybrid", label: "Hybrid" },
	{ value: "remote", label: "Remote" },
];

export const interviewAttendanceOptions: SelectOption[] = [
	{ value: "on-site", label: "On-site" },
	{ value: "remote", label: "Remote" },
];

export const updateTypeOptions: SelectOption[] = [
	{ value: "received", label: "Received" },
	{ value: "sent", label: "Sent" },
];

export const interviewTypeOptions: SelectOption[] = [
	{ value: "HR", label: "HR Interview" },
	{ value: "Technical", label: "Technical Interview" },
	{ value: "Management", label: "Management Interview" },
	{ value: "Panel", label: "Panel Interview" },
	{ value: "Phone", label: "Phone Interview" },
	{ value: "Video", label: "Video Interview" },
	{ value: "Assessment", label: "Assessment/Test" },
	{ value: "Final", label: "Final Interview" },
	{ value: "Other", label: "Other" },
];
