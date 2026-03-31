import React, { JSX } from "react";
import { SelectWidgetPreviewConfig } from "../widgets/SelectWidget";
import {
	applicationStatusOptions,
	appliedViaOptions,
	attendanceTypeOptions,
	GroupedSelectOption,
	interviewAttendanceOptions,
	interviewTypeOptions,
	scrapingFilterOperatorOptions,
	scrapingFilterTypeOptions,
	SelectOption,
	sourceTypeOptions,
	updateTypeOptions,
} from "./FormOptions";
import { DataModalHandle } from "../../DataModal/DataModal";
import { EnrichedJobData } from "../../../services/schemas/DataTables";
import { DataContextValue } from "../../../contexts/DataContext";

export interface ModalFormField {
	name: string | string[];
	secondaryName?: string;
	label?: string | JSX.Element | null;
	icon?: string;
	type: string;
	required?: boolean;
	placeholder?: string;
	options?: SelectOption[] | GroupedSelectOption[];
	validation?: (value: string) => string | null;
	liveValidation?: (value: any, formData: any, dataContext: DataContextValue) => string | null;
	rows?: number;
	isSearchable?: boolean;
	isMulti?: boolean;
	isClearable?: boolean;
	step?: string;
	maxRating?: number;
	autoComplete?: string;
	helpText?: string | null;
	addButton?: {
		modalRef: React.RefObject<DataModalHandle | null>;
		transformParentData?: ((parentData: any) => any) | null;
	};
	tabIndex?: number;
	displayCondition?: (item: any) => boolean;
	previewConfig?: SelectWidgetPreviewConfig | null;
	isDisabled?: boolean;
	autoHeight?: boolean;
	maxChars?: number;
}

interface FormFieldOverride extends Partial<ModalFormField> {}

export const formFields = {
	// ------------------------------------------------- BASIC FIELDS -------------------------------------------------

	title: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "title",
		label: "Title",
		type: "text",
		required: true,
		placeholder: "Enter title",
		...overrides,
	}),

	value: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "value",
		label: "Value",
		type: "textarea",
		required: true,
		...overrides,
	}),

	name: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "name",
		label: "Name",
		type: "text",
		required: true,
		placeholder: "Enter name",
		...overrides,
	}),

	description: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "description",
		label: "Description",
		type: "textarea",
		rows: 4,
		placeholder: "Enter description...",
		...overrides,
	}),

	note: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "note",
		label: "Notes",
		type: "textarea",
		rows: 4,
		placeholder: "Add your notes...",
		...overrides,
	}),

	url: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "url",
		label: "URL",
		type: "url",
		placeholder: "https://...",
		validation: (value: string): string | null => {
			if (value && !value.includes(".")) {
				return "Please enter a valid URL";
			} else {
				return null;
			}
		},
		...overrides,
	}),

	jobURl: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "url",
		label: "Job URL",
		type: "url",
		placeholder: "https://linkedin.com/jobs/123456",
		validation: (value: string) => {
			if (value && !value.includes(".")) {
				return "Please enter a valid URL";
			} else {
				return null;
			}
		},
		liveValidation: (value: string, formData: any, dataContext: DataContextValue): string | null => {
			if (!value) return null;
			const dup: EnrichedJobData | undefined = dataContext.jobs.find(
				(j: EnrichedJobData): boolean =>
					j.url?.trim().toLowerCase() === value.trim().toLowerCase() && j.id !== formData?.id
			);
			return dup ? "A job with this URL already exists" : null;
		},
		...overrides,
	}),

	datetime: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "date",
		label: "Date & Time",
		type: "datetime-local",
		required: true,
		...overrides,
	}),

	deadline: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "deadline",
		label: "Application Deadline",
		type: "date",
		...overrides,
	}),

	updateType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "type",
		label: "Update Type",
		type: "select",
		required: true,
		options: updateTypeOptions,
		...overrides,
	}),

	isActive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "is_active",
		label: "Active",
		type: "checkbox",
		...overrides,
	}),

	caseSensitive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "case_sensitive",
		label: "Case Sensitive",
		type: "checkbox",
		...overrides,
	}),

	isRecruiter: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "is_recruiter",
		label: "Is Recruiter",
		type: "checkbox",
		...overrides,
	}),

	// ------------------------------------------------- USERS ------------------------------------------------

	isAdmin: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "is_admin",
		label: "Admin",
		type: "checkbox",
		...overrides,
	}),

	premiumActive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: ["premium", "is_active"],
		label: "Premium Active",
		type: "toggle",
		...overrides,
	}),

	jobScrapingActive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: ["premium", "job_scraping_active"],
		label: "Job Scraping Active",
		type: "toggle",
		...overrides,
	}),

	jobRatingActive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: ["premium", "job_rating_active"],
		label: "Job Rating Active",
		type: "toggle",
		...overrides,
	}),

	password: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "password",
		label: "Password",
		type: "password",
		required: true,
		...overrides,
	}),

	// ------------------------------------------------- PERSON FIELDS ------------------------------------------------

	firstName: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "first_name",
		label: "First Name",
		type: "text",
		required: true,
		placeholder: "Enter first name",
		...overrides,
	}),

	lastName: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "last_name",
		label: "Last Name",
		type: "text",
		required: true,
		placeholder: "Enter last name",
		...overrides,
	}),

	email: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "email",
		label: "Email",
		type: "text",
		placeholder: "person@company.com",
		validation: (value: string) => {
			if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
				return "Please enter a valid email address";
			} else {
				return null;
			}
		},
		...overrides,
	}),

	phone: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "phone",
		label: "Phone",
		type: "tel",
		placeholder: "+44 20 7946 0958",
		...overrides,
	}),

	linkedinUrl: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "linkedin_url",
		label: "LinkedIn Profile",
		type: "text",
		placeholder: "https://linkedin.com/in/username",
		validation: (value: string) => {
			if (value && !value.includes("linkedin.com")) {
				return "Please enter a valid LinkedIn URL";
			} else {
				return null;
			}
		},
		...overrides,
	}),

	role: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "role",
		label: "Role",
		type: "text",
		...overrides,
	}),

	// ------------------------------------------------- LOCATION FIELDS -----------------------------------------------

	city: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "city",
		label: "City",
		type: "text",
		placeholder: "Enter city name",
		...overrides,
	}),

	postcode: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "postcode",
		label: "Post Code",
		type: "text",
		placeholder: "Enter post code",
		...overrides,
	}),

	country: (countries: SelectOption[] = [], overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "country",
		label: "Country",
		type: "select",
		options: countries,
		placeholder: "Search and select a country...",
		isSearchable: true,
		isClearable: true,
		...overrides,
	}),

	// ------------------------------------------------- JOB FIELDS --------------------------------------------------

	isFavourite: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "is_favourite",
		label: "Favourite",
		type: "star_toggle",
		...overrides,
	}),

	jobTitle: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "title",
		label: "Job Title",
		type: "text",
		required: true,
		placeholder: "Enter job title",
		...overrides,
	}),

	salaryMin: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "salary_min",
		label: "Minimum Salary",
		type: "salary",
		placeholder: "Enter minimum salary",
		step: "1000",
		...overrides,
	}),

	salaryMax: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "salary_max",
		label: "Maximum Salary",
		type: "salary",
		placeholder: "Enter maximum salary",
		step: "1000",
		...overrides,
	}),

	personalRating: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "personal_rating",
		label: "Personal Rating",
		type: "rating",
		maxRating: 5,
		...overrides,
	}),

	attendanceType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "attendance_type",
		label: "Attendance Type",
		type: "select",
		options: attendanceTypeOptions,
		...overrides,
	}),

	interviewAttendanceType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "attendance_type",
		label: "Attendance Type",
		type: "select",
		options: interviewAttendanceOptions,
		...overrides,
	}),

	// ------------------------------------------------- INTERVIEW FIELDS --------------------------------------------

	interviewType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "type",
		label: "Interview Type",
		type: "select",
		required: true,
		options: interviewTypeOptions,
		placeholder: "Select interview type",
		...overrides,
	}),

	// ------------------------------------------------- APPLICATION FIELDS -----------------------------------------

	applicationDate: (overrides: FormFieldOverride = {}): ModalFormField => ({
		...formFields.datetime(),
		name: "application_date",
		label: "Application Date",
		required: false,
		...overrides,
	}),

	applicationStatus: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "application_status",
		label: "Application Status",
		type: "select",
		options: applicationStatusOptions,
		...overrides,
	}),

	applicationUrl: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "application_url",
		label: "Application URL",
		type: "text",
		placeholder: "https://...",
		...overrides,
	}),

	applicationVia: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "applied_via",
		label: "Application Via",
		type: "select",
		options: appliedViaOptions,
		...overrides,
	}),

	// ------------------------------------------- SELECT FIELDS WITH OPTIONS ------------------------------------------

	company: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		name: "company_id",
		label: "Company",
		type: "select",
		placeholder: "Select or search company...",
		isSearchable: true,
		isClearable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData },
		...overrides,
	}),

	scrapedCompany: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		name: "company_id",
		secondaryName: "company",
		label: "Company",
		type: "select",
		placeholder: "Select or search company...",
		isSearchable: true,
		isClearable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData },
		...overrides,
	}),

	location: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		name: "location_id",
		label: "Location",
		type: "select",
		placeholder: "Select or search location...",
		isSearchable: true,
		isClearable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData },
		...overrides,
	}),

	scrapedLocation: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		name: "location_id",
		secondaryName: "parsed_location",
		label: "Location",
		type: "select",
		placeholder: "Select or search location...",
		isSearchable: true,
		isClearable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData },
		...overrides,
	}),

	keywords: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		name: "keywords",
		label: "Tags",
		type: "multiselect",
		placeholder: "Select or search tags...",
		isSearchable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData },
		...overrides,
	}),

	contacts: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		name: "contacts",
		label: "Contacts",
		type: "multiselect",
		placeholder: "Select or search contacts...",
		isSearchable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData },
		...overrides,
	}),

	interviewers: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		name: "interviewers",
		label: "Interviewers",
		type: "multiselect",
		isSearchable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData },
		...overrides,
	}),

	recruiter: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		name: "recruiter_id",
		label: "Recruiter",
		type: "select",
		isSearchable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData },
		...overrides,
	}),

	job: (options: SelectOption[] = [], overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "job_id",
		label: "Job",
		type: "select",
		required: true,
		placeholder: "Select a job",
		isSearchable: true,
		isClearable: false,
		options: options,
		...overrides,
	}),

	aggregator: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		name: "aggregator_id",
		label: "Aggregator",
		type: "select",
		placeholder: "Select an aggregator",
		isSearchable: true,
		isClearable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData },
		...overrides,
	}),

	sourceType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		options: sourceTypeOptions,
		name: "source_type",
		label: "Source",
		type: "select",
		placeholder: "Select source",
		isSearchable: true,
		isClearable: true,
		...overrides,
	}),

	scrapingFilterType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "type",
		label: "Filter Type",
		type: "select",
		required: true,
		placeholder: "Select filter type",
		isSearchable: true,
		isClearable: true,
		options: scrapingFilterTypeOptions,
		...overrides,
	}),

	scrapingFilterOperator: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "operator",
		label: "Operator",
		type: "select",
		required: true,
		placeholder: "Select filter type",
		isSearchable: true,
		isClearable: true,
		options: scrapingFilterOperatorOptions,
		...overrides,
	}),
};
