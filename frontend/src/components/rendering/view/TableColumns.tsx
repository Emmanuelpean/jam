import { renderFunctions, RenderParams, ViewField } from "./ViewRenders";
import { toDdMmYyyy } from "../../../utils/TimeUtils";
import { CompanyData, JobData, LocationData } from "../../../services/Schemas";
import { DataContextValue } from "../../../contexts/DataContext";

export interface TableColumn extends ViewField {
	label: string;
	sortable?: boolean;
	searchable?: boolean | ((item: any) => string);
	type?: string;
	sortField?: string | ((item: any, dataContext?: DataContextValue) => string | number) | string[];
	searchFields?: string | ((item: any, dataContext?: DataContextValue) => string) | string[];
	columnClass?: string;
}

const getCompanyText = (item: any, context?: DataContextValue): string => {
	return context?.companies.filter((company: CompanyData): boolean => company.id === item.company_id)[0]?.name || "";
};

const getLocationText = (item: any, context?: DataContextValue): string => {
	const location_name =
		context?.locations.filter((location: LocationData): boolean => location.id === item.location_id)[0]?.name || "";
	const attendance_name = item.attendance_type || "";
	return location_name + attendance_name;
};

const getJobText = (item: any, context?: DataContextValue): string => {
	return context?.jobs.filter((job: JobData): boolean => job.id === item.job_id)[0]?.name || "";
};

interface TableColumnOverrides extends Partial<TableColumn> {}

export const tableColumns = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	id: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "id",
		label: "ID",
		sortable: true,
		searchable: true,
		type: "number",
		...overrides,
	}),

	name: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "name",
		label: "Name",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	value: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "value",
		label: "Value",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.value,
		...overrides,
	}),

	title: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "title",
		label: "Title",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	description: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "description",
		label: "Description",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.description,
		...overrides,
	}),

	url: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "url",
		label: "Website",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.url,
		...overrides,
	}),

	urlGeneric: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "url",
		label: "Link",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.urlGeneric,
		...overrides,
	}),

	createdAt: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "created_at",
		label: "Date Added",
		type: "date",
		sortable: true,
		searchable: true,
		searchFields: (item: any) => toDdMmYyyy(item.created_at),
		render: (params: RenderParams) => renderFunctions._date(params, "created_at"),
		...overrides,
	}),

	note: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "note",
		label: "Notes",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.note,
		...overrides,
	}),

	date: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "date",
		label: "Date",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: (item: any) => toDdMmYyyy(item.date),
		render: (params: RenderParams) => renderFunctions._date(params, "date"),
		...overrides,
	}),

	type: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	updateType: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.updateType,
		...overrides,
	}),

	last_login: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "last_login",
		label: "Last Login",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: (item: any) => toDdMmYyyy(item.last_login),
		render: (params: RenderParams) => renderFunctions._date(params, "last_login"),
		...overrides,
	}),

	isActive: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_active",
		label: "Active",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.isActive,
		...overrides,
	}),

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	location: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "location",
		label: "Location",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: getLocationText,
		searchFields: getLocationText,
		render: renderFunctions.LocationBadge,
		...overrides,
	}),

	scrapedLocation: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "location_name",
		label: "Location",
		sortable: true,
		searchable: true,
		type: "text",
		// render: renderFunctions.scrapedLocationName,
		...overrides,
	}),

	city: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "city",
		label: "City",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	postcode: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "postcode",
		label: "Postcode",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	country: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "country",
		label: "Country",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	// --------------------------------------------------- COMPANIES ---------------------------------------------------

	companyBadge: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "CompanyBadge",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "company.name",
		searchFields: getCompanyText,
		render: renderFunctions.CompanyBadge,
		...overrides,
	}),

	scrapedCompany: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "company",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "company",
		searchFields: "company",
		...overrides,
	}),

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	persons: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "person",
		label: "Contacts",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "person.last_name",
		searchFields: "person.name",
		render: renderFunctions.ContactBadges,
		...overrides,
	}),

	personName: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "name",
		label: "Name",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "last_name",
		...overrides,
	}),

	email: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "email",
		label: "Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.email,
		...overrides,
	}),

	isAdmin: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_admin",
		label: "Admin",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.isAdmin,
		...overrides,
	}),

	toastActive: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "toast_active",
		label: "TOAST",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.toastActive,
		...overrides,
	}),

	appTheme: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "theme",
		label: "Theme",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.appTheme,
		...overrides,
	}),

	phone: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "phone",
		label: "Phone",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.phone,
		...overrides,
	}),

	role: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "role",
		label: "Role",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	linkedinUrl: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "linkedin_url",
		label: "LinkedIn",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.linkedinUrl,
		...overrides,
	}),

	interviewers: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "person",
		label: "Interviewers",
		sortable: false,
		searchable: true,
		type: "text",
		sortField: "person.last_name",
		searchFields: "person.name",
		render: (params: RenderParams) => renderFunctions.InterviewerBadges({ ...params, view: false }),
		...overrides,
	}),

	// ------------------------------------------------------ JOBS -----------------------------------------------------

	salaryRange: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "salary_range",
		label: "Salary",
		sortable: true,
		searchable: false,
		type: "text",
		sortField: "salary_min",
		render: renderFunctions.salaryRange,
		...overrides,
	}),

	personalRating: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "personal_rating",
		label: "Rating",
		sortable: true,
		type: "number",
		render: renderFunctions.personalRating,
		...overrides,
	}),

	keywords: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "keywords",
		label: "Keywords",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.KeywordBadges,
		...overrides,
	}),

	job: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job",
		label: "Job",
		sortable: true,
		searchable: true,
		searchFields: getJobText,
		sortField: getJobText,
		render: (params: RenderParams) => renderFunctions.jobBadge(params, null),
		...overrides,
	}),

	applicationStatus: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "application_status",
		label: "Status",
		sortable: true,
		searchable: true,
		render: renderFunctions.applicationStatus,
		...overrides,
	}),

	interviewCountLocation: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "interviews",
		label: "Interviews",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._interviewCount(param, "location_id"),
		...overrides,
	}),

	jobCountCompany: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "company_id"),
		...overrides,
	}),

	jobCountAggregator: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "source_id"),
		...overrides,
	}),

	jobCountLocation: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "location_id"),
		...overrides,
	}),

	jobCountKeyword: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "keywords"),
		...overrides,
	}),

	jobApplicationCountAggregator: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_applications",
		label: "Job Applications",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobApplicationCount(param, "application_aggregator_id"),
		...overrides,
	}),

	personCountCompany: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "persons",
		label: "Individuals",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._personCount(param, "company_id"),
		...overrides,
	}),

	// -------------------------------------------- CHASE-SPECIFIC COLUMNS ---------------------------------------------

	daysSinceLastUpdate: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "days_since_last_update",
		label: "Since Last Update",
		sortable: true,
		type: "number",
		render: renderFunctions.lastUpdateDays,
		...overrides,
	}),

	daysUntilDeadline: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "days_until_deadline",
		label: "Time Until Deadline",
		sortable: true,
		type: "number",
		render: renderFunctions.daysUntilDeadline,
		...overrides,
	}),

	lastUpdateType: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "last_update_type",
		label: "Last Update",
		sortable: true,
		type: "text",
		...overrides,
	}),
};
