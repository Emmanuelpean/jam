import { findItemById } from "../../../utils/Utils";
import { useMemo } from "react";
import { DataContextValue, useDataContext } from "../../../contexts/DataContext";
import { SelectWidgetPreviewConfig } from "../widgets/SelectWidget";
import { modalViewFields } from "../view/ModalFields";
import { AggregatorData, CompanyData, InterviewData, JobData, PersonData } from "../../../services/schemas/DataTables";
import Fuse, { FuseResult } from "fuse.js";

export type SelectOption = {
	value: string;
	label: string;
};

export interface GroupedSelectOption {
	label: string;
	options: SelectOption[];
}

export function findClosestOption(options: SelectOption[], name: string): number | null {
	if (!name || options.length === 0) return null;
	const fuse = new Fuse(options, { keys: ["label"], threshold: 0.4, includeScore: true });
	const results: FuseResult<SelectOption>[] = fuse.search(name);
	if (!results.length) return null;
	const value: string | undefined = results[0]?.item.value;
	return value != null ? Number(value) : null;
}

export function findExactOption(options: SelectOption[], name: string): number | null {
	if (!name || options.length === 0) return null;
	const match: SelectOption | undefined = options.find(
		(opt: SelectOption): boolean => opt.label.toLowerCase() === name.toLowerCase()
	);
	return match ? Number(match.value) : null;
}

interface UseFormOptionsReturn {
	companies: SelectOption[];
	keywords: SelectOption[];
	persons: SelectOption[];
	aggregators: SelectOption[];
	jobs: SelectOption[];
	countries: SelectOption[];
	currencies: SelectOption[];
	currencyNames: SelectOption[];
	getCompanyPreviewConfig: SelectWidgetPreviewConfig;
	getPersonPreviewConfig: SelectWidgetPreviewConfig;
	getAggregatorPreviewConfig: SelectWidgetPreviewConfig;
	getContactOptions: (job: JobData) => GroupedSelectOption[];
}

export const toSelectOptions = <T extends Record<string, any>>(
	data: T[],
	valueKey: keyof T | ((item: T) => any) = "id",
	labelKey: keyof T | ((item: T) => any) = "name"
): SelectOption[] => {
	const sorted: T[] = [...data].sort((a: T, b: T): number => {
		const aLabel: any = typeof labelKey === "function" ? labelKey(a) : a[labelKey];
		const bLabel: any = typeof labelKey === "function" ? labelKey(b) : b[labelKey];
		return String(aLabel).localeCompare(String(bLabel));
	});

	return sorted.map(
		(item: T): SelectOption => ({
			value: typeof valueKey === "function" ? valueKey(item) : item[valueKey],
			label: typeof labelKey === "function" ? labelKey(item) : item[labelKey],
		})
	);
};

export const useFormOptions = (): UseFormOptionsReturn => {
	const dataContext: DataContextValue = useDataContext();

	const getCompanyPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [modalViewFields.url(), [modalViewFields.description()]],
		getDataById: (id: number): CompanyData | null => findItemById(dataContext.companies, id),
	};

	const getPersonPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [modalViewFields.email(), [modalViewFields.companyBadge(), modalViewFields.role()]],
		getDataById: (id: number): PersonData | null => findItemById(dataContext.persons, id),
	};

	const getAggregatorPreviewConfig: SelectWidgetPreviewConfig = {
		enabled: true,
		fields: [modalViewFields.url()],
		getDataById: (id: number): AggregatorData | null => findItemById(dataContext.aggregators, id),
	};

	const getPersonLabel = (person: PersonData): string => {
		if (person.company_id) {
			const company: CompanyData | null = findItemById(dataContext.companies, person.company_id);
			if (company) {
				return `${person.name} (${company.name})`;
			}
		}
		return person.name;
	};

	const getContactOptions = (job: JobData): GroupedSelectOption[] => {
		const persons: PersonData[] = dataContext.persons.filter(
			(person: PersonData): boolean => person.email !== null
		);
		const jobContacts: PersonData[] = persons.filter((person: PersonData): boolean =>
			job.contacts?.includes(person.id)
		);
		const interviews: InterviewData[] = dataContext.interviews.filter(
			(interview: InterviewData): boolean => interview.job_id === job.id
		);
		const interviewContacts: PersonData[] = persons.filter((person: PersonData): boolean =>
			interviews.some((interview: InterviewData) => interview.interviewers?.includes(person.id))
		);
		const excludedIds = new Set<number>([
			...jobContacts.map((p: PersonData): number => p.id),
			...interviewContacts.map((p: PersonData): number => p.id),
		]);
		const otherContacts: PersonData[] = persons.filter((p: PersonData): boolean => !excludedIds.has(p.id));
		return [
			{ label: "Job Contacts", options: toSelectOptions(jobContacts, "id", getPersonLabel) },
			{
				label: "Interviewers",
				options: toSelectOptions(interviewContacts, "id", getPersonLabel),
			},
			{ label: "Other Contacts", options: toSelectOptions(otherContacts, "id", getPersonLabel) },
		];
	};

	// Convert data to SelectOptions and memoize
	const companyOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(dataContext.companies),
		[dataContext.companies]
	);
	const keywordOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(dataContext.keywords),
		[dataContext.keywords]
	);
	const personOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(dataContext.persons, "id", getPersonLabel),
		[dataContext.persons]
	);
	const aggregatorOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(dataContext.aggregators),
		[dataContext.aggregators]
	);
	const jobOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(dataContext.jobs, "id", "name"),
		[dataContext.jobs]
	);
	const countryOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(dataContext.countries, "name", "name"),
		[dataContext.countries]
	);
	const currencyOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(dataContext.currencies, "code", "symbol"),
		[dataContext.currencies]
	);
	const currencyNameOptions: SelectOption[] = useMemo(
		(): SelectOption[] => toSelectOptions(dataContext.currencies, "code", "name"),
		[dataContext.currencies]
	);

	return {
		companies: companyOptions,
		keywords: keywordOptions,
		persons: personOptions,
		aggregators: aggregatorOptions,
		jobs: jobOptions,
		countries: countryOptions,
		currencies: currencyOptions,
		currencyNames: currencyNameOptions,
		getCompanyPreviewConfig,
		getPersonPreviewConfig,
		getAggregatorPreviewConfig,
		getContactOptions,
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
	{ value: "HR", label: "HR" },
	{ value: "Technical", label: "Technical" },
	{ value: "Management", label: "Management" },
	{ value: "Panel", label: "Panel" },
	{ value: "Phone", label: "Phone" },
	{ value: "Video", label: "Video" },
	{ value: "Assessment", label: "Assessment/Test" },
	{ value: "Final", label: "Final" },
	{ value: "Other", label: "Other" },
];

export const scrapingFilterTypeOptions: SelectOption[] = [
	{ value: "title", label: "Job Title" },
	{ value: "company", label: "Company Name" },
	{ value: "location", label: "Location" },
	{ value: "salary_min", label: "Minimum Salary" },
	{ value: "salary_max", label: "Maximum Salary" },
	{ value: "attendance_type", label: "Attendance Type" },
];

export const scrapingFilterOperatorOptions: SelectOption[] = [
	{ value: "contains", label: "Contains" },
	{ value: "equals", label: "Equals To" },
	{ value: "starts_with", label: "Starts With" },
	{ value: "ends_with", label: "Ends With" },
	{ value: "less_than", label: "Less or Equal Than" },
	{ value: "greater_than", label: "Greater or Equal Than" },
	{ value: "not_contains", label: "Does Not Contain" },
	{ value: "not_equals", label: "Is Not Equal To" },
];

export const sourceTypeOptions: SelectOption[] = [
	{ value: "aggregator", label: "Aggregator" },
	{ value: "aggregator_email", label: "Aggregator Email Alert" },
	{ value: "recruiter", label: "Recruiter" },
	{ value: "recruitment_company", label: "Recruitment Company" },
	{ value: "other", label: "Other" },
];
