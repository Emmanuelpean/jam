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
import { EnrichedJobData, JobData } from "../../../services/schemas/DataTables";
import { DataContextValue } from "../../../contexts/DataContext";

export interface ModalFormField {
	key: string | string[];
	secondaryKey?: string;
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
		id?: string;
	};
	tabIndex?: number;
	displayCondition?: (item: any) => boolean;
	previewConfig?: SelectWidgetPreviewConfig | null;
	isDisabled?: boolean;
	highlight?: boolean;
	autoHeight?: boolean;
	maxChars?: number;
	fileType?: string;
}

interface FormFieldOverride extends Partial<ModalFormField> {}

export const formFields = {
	// ------------------------------------------------- BASIC FIELDS -------------------------------------------------

	title: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "title",
		label: "Title",
		type: "text",
		required: true,
		placeholder: "Enter title",
		...overrides,
	}),

	value: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "value",
		label: "Value",
		type: "textarea",
		required: true,
		...overrides,
	}),

	name: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "name",
		label: "Name",
		type: "text",
		required: true,
		placeholder: "Enter name",
		...overrides,
	}),

	description: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "description",
		label: "Description",
		type: "textarea",
		rows: 4,
		placeholder: "Enter description...",
		...overrides,
	}),

	note: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "note",
		label: "Notes",
		type: "textarea",
		rows: 4,
		placeholder: "Add your notes...",
		...overrides,
	}),

	url: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "url",
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
		key: "url",
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

	location: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "location",
		label: "Location",
		type: "text",
		placeholder: "e.g. London, UK",
		isClearable: true,
		displayCondition: (formData: JobData): boolean => {
			return formData.attendance_type !== "remote";
		},
		...overrides,
	}),

	datetime: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "date",
		label: "Date & Time",
		type: "datetime-local",
		required: true,
		...overrides,
	}),

	deadline: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "deadline",
		label: "Application Deadline",
		type: "date",
		...overrides,
	}),

	updateType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "type",
		label: "Update Type",
		type: "select",
		required: true,
		options: updateTypeOptions,
		...overrides,
	}),

	isActive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "is_active",
		label: "Active",
		type: "checkbox",
		...overrides,
	}),

	caseSensitive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "case_sensitive",
		label: "Case Sensitive",
		type: "checkbox",
		...overrides,
	}),

	isRecruiter: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "is_recruiter",
		label: "Is Recruiter",
		type: "checkbox",
		...overrides,
	}),

	// ------------------------------------------------- USERS ------------------------------------------------

	isAdmin: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "is_admin",
		label: "Admin",
		type: "checkbox",
		...overrides,
	}),

	premiumActive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: ["premium", "is_active"],
		label: "Premium Active",
		type: "toggle",
		...overrides,
	}),

	jobScrapingActive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: ["premium", "job_scraping_active"],
		label: "Job Scraping Active",
		type: "toggle",
		...overrides,
	}),

	jobRatingActive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: ["premium", "job_rating_active"],
		label: "Job Rating Active",
		type: "toggle",
		...overrides,
	}),

	password: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "password",
		label: "Password",
		type: "password",
		required: true,
		...overrides,
	}),

	// ------------------------------------------------- PERSON FIELDS ------------------------------------------------

	firstName: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "first_name",
		label: "First Name",
		type: "text",
		required: true,
		placeholder: "Enter first name",
		...overrides,
	}),

	lastName: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "last_name",
		label: "Last Name",
		type: "text",
		required: true,
		placeholder: "Enter last name",
		...overrides,
	}),

	email: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "email",
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
		key: "phone",
		label: "Phone",
		type: "tel",
		placeholder: "+44 20 7946 0958",
		...overrides,
	}),

	linkedinUrl: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "linkedin_url",
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
		key: "role",
		label: "Role",
		type: "text",
		...overrides,
	}),

	// ------------------------------------------------- LOCATION FIELDS -----------------------------------------------

	city: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "city",
		label: "City",
		type: "text",
		placeholder: "Enter city name",
		...overrides,
	}),

	postcode: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "postcode",
		label: "Post Code",
		type: "text",
		placeholder: "Enter post code",
		...overrides,
	}),

	// ------------------------------------------------- JOB FIELDS --------------------------------------------------

	isFavourite: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "is_favourite",
		label: "Favourite",
		type: "star_toggle",
		...overrides,
	}),

	jobTitle: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "title",
		label: "Job Title",
		type: "text",
		required: true,
		placeholder: "Enter job title",
		...overrides,
	}),

	salaryMin: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "salary_min",
		label: "Minimum Salary",
		type: "salary",
		placeholder: "35000",
		step: "1000",
		...overrides,
	}),

	salaryMax: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "salary_max",
		label: "Maximum Salary",
		type: "salary",
		placeholder: "45000",
		step: "1000",
		...overrides,
	}),

	personalRating: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "personal_rating",
		label: "Personal Rating",
		type: "rating",
		maxRating: 5,
		...overrides,
	}),

	attendanceType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "attendance_type",
		label: "Attendance Type",
		type: "select",
		options: attendanceTypeOptions,
		...overrides,
	}),

	interviewAttendanceType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "attendance_type",
		label: "Attendance Type",
		type: "select",
		options: interviewAttendanceOptions,
		...overrides,
	}),

	// ------------------------------------------------- INTERVIEW FIELDS --------------------------------------------

	interviewType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "type",
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
		key: "application_date",
		label: "Application Date",
		required: false,
		...overrides,
	}),

	applicationStatus: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "application_status",
		label: "Application Status",
		type: "select",
		options: applicationStatusOptions,
		...overrides,
	}),

	applicationUrl: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "application_url",
		label: "Application URL",
		type: "text",
		placeholder: "https://...",
		...overrides,
	}),

	applicationVia: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "applied_via",
		label: "Application Via",
		type: "select",
		options: appliedViaOptions,
		...overrides,
	}),

	cvUpload: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "cv_id",
		label: "CV",
		type: "file_upload",
		fileType: "cv",
		...overrides,
	}),

	coverLetterUpload: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "cover_letter_id",
		label: "Cover Letter",
		type: "cover_letter",
		fileType: "cover_letter",
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
		key: "company_id",
		label: "Company",
		type: "select",
		placeholder: "Select or search company...",
		isSearchable: true,
		isClearable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData, id: "add-button-company" },
		...overrides,
	}),

	scrapedCompany: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		key: "company_id",
		secondaryKey: "company",
		label: "Company",
		type: "select",
		placeholder: "Select or search company...",
		isSearchable: true,
		isClearable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData, id: "add-button-company" },
		...overrides,
	}),

	keywords: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		key: "keywords",
		label: "Tags",
		type: "multiselect",
		placeholder: "Select or search tags...",
		isSearchable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData, id: "add-button-keyword" },
		...overrides,
	}),

	contacts: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		key: "contacts",
		label: "Contacts",
		type: "multiselect",
		placeholder: "Select or search contacts...",
		isSearchable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData, id: "add-button-contact" },
		...overrides,
	}),

	interviewers: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		key: "interviewers",
		label: "Interviewers",
		type: "multiselect",
		isSearchable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData, id: "add-button-interviewer" },
		...overrides,
	}),

	recruiter: (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		key: "recruiter_id",
		label: "Recruiter",
		type: "select",
		isSearchable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData, id: "add-button-recruiter" },
		...overrides,
	}),

	job: (options: SelectOption[] = [], overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "job_id",
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
		key: "aggregator_id",
		label: "Aggregator",
		type: "select",
		placeholder: "Select an aggregator",
		isSearchable: true,
		isClearable: true,
		previewConfig: previewConfig,
		options: options,
		addButton: { modalRef, transformParentData, id: "add-button-aggregator" },
		...overrides,
	}),

	sourceType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		options: sourceTypeOptions,
		key: "source_type",
		label: "Source",
		type: "select",
		placeholder: "Select source",
		isSearchable: true,
		isClearable: true,
		...overrides,
	}),

	sourceGroup: (
		aggregators: SelectOption[],
		aggregatorModalRef: React.RefObject<DataModalHandle | null>,
		getAggregatorPreviewConfig: SelectWidgetPreviewConfig | null,
		persons: SelectOption[],
		personModalRef: React.RefObject<DataModalHandle | null>,
		getPersonPreviewConfig: SelectWidgetPreviewConfig | null,
		companies: SelectOption[],
		companyModalRef: React.RefObject<DataModalHandle | null>,
		getCompanyPreviewConfig: SelectWidgetPreviewConfig | null,
		aggregatorTransformParentData: ((parentData: any) => any) | null = null
	): ModalFormField[] => [
		formFields.sourceType(),
		formFields.aggregator(
			aggregators,
			aggregatorModalRef,
			aggregatorTransformParentData,
			getAggregatorPreviewConfig,
			{
				key: "source_aggregator_id",
				displayCondition: (formData: any): boolean =>
					["aggregator", "aggregator_email"].includes(formData.source_type || ""),
			}
		),
		formFields.recruiter(persons, personModalRef, null, getPersonPreviewConfig, {
			displayCondition: (formData: any): boolean => formData.source_type === "recruiter",
		}),
		formFields.company(companies, companyModalRef, null, getCompanyPreviewConfig, {
			key: "recruitment_company_id",
			displayCondition: (formData: any): boolean => formData.source_type === "recruitment_company",
		}),
	],

	scrapingFilterType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "type",
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
		key: "operator",
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
