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
import { useConfig } from "../../../contexts/ConfigContext";
import { ColumnLimits } from "../../../services/schemas/Base";

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
	size?: "sm";
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

export const EmailValidation = (value: string): string | null => {
	if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
		return "Email format is invalid";
	} else {
		return null;
	}
};

export interface FormFieldOverride extends Partial<ModalFormField> {}

const createFormFields = (limits: Partial<ColumnLimits>) => {
	// ------------------------------------------------- BASIC FIELDS -------------------------------------------------

	const titleField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "title",
		label: "Title",
		type: "text",
		required: true,
		placeholder: "Enter title",
		maxChars: limits.job_title,
		...overrides,
	});

	const valueField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "value",
		label: "Value",
		type: "textarea",
		required: true,
		...overrides,
	});

	const nameField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "name",
		label: "Name",
		type: "text",
		required: true,
		placeholder: "Enter name",
		maxChars: limits.name,
		...overrides,
	});

	const descriptionField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "description",
		label: "Description",
		type: "textarea",
		rows: 4,
		placeholder: "Enter description...",
		maxChars: limits.description,
		...overrides,
	});

	const fileNameField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "filename",
		label: "Filename",
		type: "text",
		required: true,
		placeholder: "Enter filename",
		maxChars: limits.file_name,
		...overrides,
	});

	const noteField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "note",
		label: "Notes",
		type: "textarea",
		rows: 4,
		placeholder: "Add your notes...",
		maxChars: limits.note,
		...overrides,
	});

	const urlField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "url",
		label: "URL",
		type: "url",
		placeholder: "https://...",
		maxChars: limits.url,
		...overrides,
	});

	const jobUrlField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "url",
		label: "Job URL",
		type: "url",
		placeholder: "https://linkedin.com/jobs/123456",
		maxChars: limits.url,
		liveValidation: (value: string, formData: any, dataContext: DataContextValue): string | null => {
			if (!value) return null;
			const dup: EnrichedJobData | undefined = dataContext.jobs.find(
				(j: EnrichedJobData): boolean =>
					j.url?.trim().toLowerCase() === value.trim().toLowerCase() && j.id !== formData?.id
			);
			return dup ? "A job with this URL already exists" : null;
		},
		...overrides,
	});

	const locationField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "location",
		label: "Location",
		type: "text",
		placeholder: "e.g. London, UK",
		maxChars: limits.location,
		isClearable: true,
		displayCondition: (formData: JobData): boolean => {
			return formData.attendance_type !== "remote";
		},
		...overrides,
	});

	const datetimeField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "date",
		label: "Date & Time",
		type: "datetime-local",
		required: true,
		...overrides,
	});

	const deadlineField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "deadline",
		label: "Application Deadline",
		type: "date",
		...overrides,
	});

	const updateTypeField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "type",
		label: "Update Type",
		type: "select",
		required: true,
		options: updateTypeOptions,
		...overrides,
	});

	const isActiveField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "is_active",
		label: "Active",
		type: "checkbox",
		...overrides,
	});

	const caseSensitiveField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "case_sensitive",
		label: "Case Sensitive",
		type: "checkbox",
		...overrides,
	});

	const isRecruiterField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "is_recruiter",
		label: "Is Recruiter",
		type: "checkbox",
		...overrides,
	});

	// ------------------------------------------------- USER FIELDS ------------------------------------------------

	const isAdminField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "is_admin",
		label: "Admin",
		type: "checkbox",
		...overrides,
	});

	const premiumActiveField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: ["premium", "is_active"],
		label: "Premium Active",
		type: "toggle",
		...overrides,
	});

	const jobScrapingActiveField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: ["premium", "job_scraping_active"],
		label: "Job Scraping Active",
		type: "toggle",
		...overrides,
	});

	const jobRatingActiveField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: ["premium", "job_rating_active"],
		label: "Job Rating Active",
		type: "toggle",
		...overrides,
	});

	const passwordField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "password",
		label: "Password",
		type: "password",
		required: true,
		maxChars: limits.password,
		...overrides,
	});

	// ------------------------------------------------- PERSON FIELDS ------------------------------------------------

	const firstNameField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "first_name",
		label: "First Name",
		type: "text",
		required: true,
		placeholder: "Enter first name",
		maxChars: limits.first_name,
		...overrides,
	});

	const lastNameField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "last_name",
		label: "Last Name",
		type: "text",
		required: true,
		placeholder: "Enter last name",
		maxChars: limits.last_name,
		...overrides,
	});

	const emailField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "email",
		label: "Email",
		type: "text",
		placeholder: "person@company.com",
		maxChars: limits.email,
		validation: EmailValidation,
		...overrides,
	});

	const phoneField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "phone",
		label: "Phone",
		type: "tel",
		placeholder: "+44 20 7946 0958",
		maxChars: limits.phone,
		...overrides,
	});

	const linkedinUrlField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "linkedin_url",
		label: "LinkedIn Profile",
		type: "text",
		placeholder: "https://linkedin.com/in/username",
		maxChars: limits.url,
		validation: (value: string) => {
			if (value && !value.includes("linkedin")) {
				return "Please enter a valid LinkedIn URL";
			} else {
				return null;
			}
		},
		...overrides,
	});

	const roleField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "role",
		label: "Role",
		type: "text",
		maxChars: limits.role,
		...overrides,
	});

	// ------------------------------------------------- LOCATION FIELDS -----------------------------------------------

	const cityField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "city",
		label: "City",
		type: "text",
		placeholder: "Enter city name",
		...overrides,
	});

	const postcodeField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "postcode",
		label: "Post Code",
		type: "text",
		placeholder: "Enter post code",
		...overrides,
	});

	// ------------------------------------------------- JOB FIELDS --------------------------------------------------

	const isFavouriteField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "is_favourite",
		label: "Favourite",
		type: "star_toggle",
		...overrides,
	});

	const jobTitleField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "title",
		label: "Job Title",
		type: "text",
		required: true,
		placeholder: "Enter job title",
		maxChars: limits.job_title,
		...overrides,
	});

	const salaryMinField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "salary_min",
		label: "Minimum Salary",
		type: "salary",
		placeholder: "35000",
		step: "1000",
		liveValidation: (value: string) => {
			return value && isNaN(Number(value)) ? "Minimum Salary must be a valid number" : null;
		},
		...overrides,
	});

	const salaryMaxField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "salary_max",
		label: "Maximum Salary",
		type: "salary",
		placeholder: "45000",
		step: "1000",
		liveValidation: (value: string) => {
			return value && isNaN(Number(value)) ? "Maximum Salary must be a valid number" : null;
		},
		...overrides,
	});

	const personalRatingField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "personal_rating",
		label: "Personal Rating",
		type: "rating",
		maxRating: 5,
		...overrides,
	});

	const attendanceTypeField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "attendance_type",
		label: "Attendance Type",
		type: "select",
		options: attendanceTypeOptions,
		...overrides,
	});

	const interviewAttendanceTypeField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "attendance_type",
		label: "Attendance Type",
		type: "select",
		options: interviewAttendanceOptions,
		...overrides,
	});

	// ------------------------------------------------- INTERVIEW FIELDS --------------------------------------------

	const interviewTypeField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "type",
		label: "Interview Type",
		type: "select",
		required: true,
		options: interviewTypeOptions,
		placeholder: "Select interview type",
		...overrides,
	});

	// ------------------------------------------------- APPLICATION FIELDS -----------------------------------------

	const applicationDateField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		...datetimeField(),
		key: "application_date",
		label: "Application Date",
		required: false,
		...overrides,
	});

	const applicationStatusField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "application_status",
		label: "Application Status",
		type: "select",
		options: applicationStatusOptions,
		...overrides,
	});

	const applicationUrlField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "application_url",
		label: "Application URL",
		type: "text",
		placeholder: "https://...",
		maxChars: limits.url,
		...overrides,
	});

	const applicationViaField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "applied_via",
		label: "Application Via",
		type: "select",
		options: appliedViaOptions,
		...overrides,
	});

	const cvUploadField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "cv_id",
		label: "CV",
		type: "file_upload",
		fileType: "cv",
		...overrides,
	});

	const coverLetterUploadField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "cover_letter_id",
		label: "Cover Letter",
		type: "cover_letter",
		fileType: "cover_letter",
		...overrides,
	});

	// ------------------------------------------- SELECT FIELDS WITH OPTIONS ------------------------------------------

	const companyField = (
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
	});

	const scrapedCompanyField = (
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
	});

	const keywordsField = (
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
	});

	const contactsField = (
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
	});

	const interviewersField = (
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
	});

	const recruiterField = (
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
	});

	const jobField = (options: SelectOption[] = [], overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "job_id",
		label: "Job",
		type: "select",
		required: true,
		placeholder: "Select a job",
		isSearchable: true,
		isClearable: false,
		options: options,
		...overrides,
	});

	const aggregatorField = (
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
	});

	const applicationAggregatorField = (
		options: SelectOption[] = [],
		modalRef: React.RefObject<DataModalHandle | null>,
		transformParentData?: ((parentData: any) => any) | null,
		previewConfig: SelectWidgetPreviewConfig | null = null,
		overrides: FormFieldOverride = {}
	): ModalFormField => ({
		...aggregatorField(options, modalRef, transformParentData, previewConfig),
		key: "application_aggregator_id",
		displayCondition: (formData: { applied_via: string | null }): boolean =>
			formData.applied_via ? formData.applied_via === "aggregator" : false,
		...overrides,
	});

	const sourceTypeField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		options: sourceTypeOptions,
		key: "source_type",
		label: "Source",
		type: "select",
		placeholder: "Select source",
		isSearchable: true,
		isClearable: true,
		...overrides,
	});

	const sourceGroupFields = (
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
		sourceTypeField(),
		aggregatorField(aggregators, aggregatorModalRef, aggregatorTransformParentData, getAggregatorPreviewConfig, {
			key: "source_aggregator_id",
			displayCondition: (formData: any): boolean =>
				["aggregator", "aggregator_email"].includes(formData.source_type || ""),
		}),
		recruiterField(persons, personModalRef, null, getPersonPreviewConfig, {
			displayCondition: (formData: any): boolean => formData.source_type === "recruiter",
		}),
		companyField(companies, companyModalRef, null, getCompanyPreviewConfig, {
			key: "recruitment_company_id",
			displayCondition: (formData: any): boolean => formData.source_type === "recruitment_company",
		}),
	];

	const scrapingFilterTypeField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "type",
		label: "Filter Type",
		type: "select",
		required: true,
		placeholder: "Select filter type",
		isSearchable: true,
		isClearable: true,
		options: scrapingFilterTypeOptions,
		...overrides,
	});

	const scrapingFilterOperatorField = (overrides: FormFieldOverride = {}): ModalFormField => ({
		key: "operator",
		label: "Operator",
		type: "select",
		required: true,
		placeholder: "Select filter type",
		isSearchable: true,
		isClearable: true,
		options: scrapingFilterOperatorOptions,
		...overrides,
	});

	return {
		titleField,
		valueField,
		nameField,
		descriptionField,
		fileNameField,
		noteField,
		urlField,
		jobUrlField,
		locationField,
		datetimeField,
		deadlineField,
		updateTypeField,
		isActiveField,
		caseSensitiveField,
		isRecruiterField,
		isAdminField,
		premiumActiveField,
		jobScrapingActiveField,
		jobRatingActiveField,
		passwordField,
		firstNameField,
		lastNameField,
		emailField,
		phoneField,
		linkedinUrlField,
		roleField,
		cityField,
		postcodeField,
		isFavouriteField,
		jobTitleField,
		salaryMinField,
		salaryMaxField,
		personalRatingField,
		attendanceTypeField,
		interviewAttendanceTypeField,
		interviewTypeField,
		applicationDateField,
		applicationStatusField,
		applicationUrlField,
		applicationViaField,
		cvUploadField,
		coverLetterUploadField,
		companyField,
		scrapedCompanyField,
		keywordsField,
		contactsField,
		interviewersField,
		recruiterField,
		jobField,
		aggregatorField,
		applicationAggregatorField,
		sourceTypeField,
		sourceGroupFields,
		scrapingFilterTypeField,
		scrapingFilterOperatorField,
	};
};

export const useFormFields = () => {
	const { config } = useConfig();
	const limits = config?.column_limits ?? {};
	return createFormFields(limits);
};
