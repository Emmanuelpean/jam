import { ReactNode } from "react";
import { renderFunctions, RenderParams } from "./ViewRenders";
import { localeDateOnly } from "../../../utils/TimeUtils";

interface TableColumnOverrides {
	key?: string;
	label?: string;
	sortable?: boolean;
	searchable?: boolean | ((item: any) => string);
	type?: string;
	render?: (params: RenderParams) => ReactNode;
	sortField?: string;
	searchFields?: string | ((item: any) => string);
	columnClass?: string;
	accessKey?: string | undefined;
}

export interface TableColumn {
	key: string;
	label: string;
	sortable?: boolean;
	searchable?: boolean | ((item: any) => string);
	type?: string;
	render?: (params: RenderParams) => ReactNode;
	sortField?: string;
	searchFields?: string | ((item: any) => string);
	columnClass?: string;
	accessKey?: string | undefined;
}

type TableColumnFactory = (overrides?: TableColumnOverrides) => TableColumn;

interface Columns {
	[key: string]: TableColumnFactory;
}

export const tableColumns: Columns = {
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

	createdAt: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "created_at",
		label: "Date Added",
		type: "date",
		sortable: true,
		searchable: true,
		searchFields: (item: any) => localeDateOnly(item.created_at),
		render: renderFunctions.createdDate,
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
		searchFields: (item: any) => localeDateOnly(item.date),
		render: renderFunctions.date,
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
		searchFields: (item: any) => localeDateOnly(item.last_login),
		render: renderFunctions.lastLogin,
		...overrides,
	}),

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	location: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "location",
		label: "Location",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "location.name", // TODO search by attendance_type too
		searchFields: "location.name", // TODO filter by attendance_type too
		render: renderFunctions.locationBadge,
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

	company: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "company",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "company.name",
		searchFields: "company.name",
		render: renderFunctions.companyBadge,
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
		render: renderFunctions.contactBadges,
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
		searchable: true,
		type: "text",
		render: renderFunctions.isAdmin,
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
		render: (params: RenderParams) => renderFunctions.interviewerBadges({ ...params, view: false }),
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
		key: "keywordBadges",
		label: "Keywords",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.keywordBadges,
		...overrides,
	}),

	job: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job",
		label: "Job",
		sortable: true,
		searchable: true,
		searchFields: "job.name",
		sortField: "job.name",
		render: renderFunctions.jobNameBadge,
		...overrides,
	}),

	status: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "status",
		label: "Status",
		sortable: true,
		searchable: true,
		render: renderFunctions.status,
		...overrides,
	}),

	interviewCount: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "interviews",
		label: "Interviews",
		sortable: true,
		searchable: false,
		render: renderFunctions.interviewCount,
		...overrides,
	}),

	updateCount: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "updates",
		label: "Updates",
		sortable: true,
		searchable: false,
		render: renderFunctions.updateCount,
		...overrides,
	}),

	jobCount: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		render: renderFunctions.jobCount,
		...overrides,
	}),

	jobApplicationCount: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_applications",
		label: "Job Applications",
		sortable: true,
		searchable: false,
		render: renderFunctions.jobApplicationCount,
		...overrides,
	}),

	personCount: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "persons",
		label: "Individuals",
		sortable: true,
		searchable: false,
		render: renderFunctions.personCount,
		...overrides,
	}),

	// -------------------------------------------- CHASE-SPECIFIC COLUMNS ---------------------------------------------

	daysSinceLastUpdate: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "days_since_last_update",
		label: "Days Since Last Update",
		sortable: true,
		type: "number",
		render: renderFunctions.lastUpdateDays,
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
