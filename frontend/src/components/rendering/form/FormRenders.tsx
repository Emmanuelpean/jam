import { JSX } from "react";
import { Theme, THEMES } from "../../../utils/Theme";
import { SelectOption } from "../../../utils/Utils";
import { JobData } from "../../../services/Schemas";

export interface ModalFormField {
	name: string;
	label?: string | JSX.Element;
	icon?: string;
	type: string;
	required?: boolean;
	placeholder?: string;
	options?: SelectOption[];
	validation?: (value: string) => { isValid: boolean; message: string } | undefined;
	rows?: number;
	isSearchable?: boolean;
	isMulti?: boolean;
	isClearable?: boolean;
	step?: string;
	maxRating?: number;
	autoComplete?: string;
	helpText?: string | null;
	addButton?: { onClick?: () => void };
	tabIndex?: number;
	displayCondition?: (item: any) => boolean;
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
		type: "text",
		placeholder: "https://...",
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
		options: [
			{ value: "received", label: "Received" },
			{ value: "sent", label: "Sent" },
		],
		...overrides,
	}),

	isActive: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "is_active",
		label: "Active",
		type: "checkbox",
		...overrides,
	}),

	// ------------------------------------------------- USERS ------------------------------------------------

	appTheme: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "theme",
		label: "App Theme",
		type: "select",
		options: THEMES.map((theme: Theme): SelectOption => ({ value: theme.key, label: theme.name })),
		...overrides,
	}),

	isAdmin: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "is_admin",
		label: "Admin",
		type: "checkbox",
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
				return { isValid: false, message: "Please enter a valid email address" };
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
				return { isValid: false, message: "Please enter a valid LinkedIn URL" };
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
		options: [
			{ value: "on-site", label: "On-site" },
			{ value: "hybrid", label: "Hybrid" },
			{ value: "remote", label: "Remote" },
		],
		...overrides,
	}),

	interviewAttendanceType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "attendance_type",
		label: "Attendance Type",
		type: "select",
		options: [
			{ value: "on-site", label: "On-site" },
			{ value: "remote", label: "Remote" },
		],
		...overrides,
	}),

	// ------------------------------------------------- INTERVIEW FIELDS --------------------------------------------

	interviewType: (overrides: FormFieldOverride = {}): ModalFormField => ({
		name: "type",
		label: "Interview Type",
		type: "select",
		required: true,
		options: [
			{ value: "HR", label: "HR Interview" },
			{ value: "Technical", label: "Technical Interview" },
			{ value: "Management", label: "Management Interview" },
			{ value: "Panel", label: "Panel Interview" },
			{ value: "Phone", label: "Phone Interview" },
			{ value: "Video", label: "Video Interview" },
			{ value: "Assessment", label: "Assessment/Test" },
			{ value: "Final", label: "Final Interview" },
			{ value: "Other", label: "Other" },
		],
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
		options: [
			{ value: "applied", label: "Applied" },
			{ value: "interview", label: "Interview" },
			{ value: "rejected", label: "Rejected" },
			{ value: "offer", label: "Offer" },
			{ value: "withdrawn", label: "Withdrawn" },
		],
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
		options: [
			{ value: "aggregator", label: "Aggregator" },
			{ value: "email", label: "Email" },
			{ value: "phone", label: "Phone" },
			{ value: "other", label: "Other" },
		],
		...overrides,
	}),

	// ------------------------------------------- SELECT FIELDS WITH OPTIONS ------------------------------------------

	company: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: FormFieldOverride = {},
	): ModalFormField => ({
		name: "company_id",
		label: "Company",
		type: "select",
		placeholder: "Select or search company...",
		isSearchable: true,
		isClearable: true,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	location: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: FormFieldOverride = {},
	): ModalFormField => ({
		name: "location_id",
		label: "Location",
		type: "select",
		placeholder: "Select or search location...",
		isSearchable: true,
		isClearable: true,
		displayCondition: (formData: JobData): boolean => {
			return formData.attendance_type ? formData.attendance_type === "on-site" : true;
		},
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	keywords: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: FormFieldOverride = {},
	): ModalFormField => ({
		name: "keywords",
		label: "Tags",
		type: "multiselect",
		placeholder: "Select or search tags...",
		isSearchable: true,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	contacts: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: FormFieldOverride = {},
	): ModalFormField => ({
		name: "contacts",
		label: "Contacts",
		type: "multiselect",
		placeholder: "Select or search contacts...",
		isSearchable: true,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),

	interviewers: (
		options: SelectOption[] = [],
		onAdd: (() => void) | null = null,
		overrides: FormFieldOverride = {},
	): ModalFormField => ({
		name: "interviewers",
		label: "Interviewers",
		type: "multiselect",
		isSearchable: true,
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
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
		onAdd: (() => void) | null = null,
		overrides: FormFieldOverride = {},
	): ModalFormField => ({
		name: "aggregator_id",
		label: "Aggregator",
		type: "select",
		placeholder: "Select an aggregator",
		isSearchable: true,
		isClearable: true,
		displayCondition: (formData: any): boolean => {
			return formData.applied_via ? formData.applied_via === "aggregator" : true;
		},
		options: options,
		...(onAdd && {
			addButton: {
				onClick: onAdd,
			},
		}),
		...overrides,
	}),
};
