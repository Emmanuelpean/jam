import { renderFunctions, RenderParams, ViewField } from "./ViewRenders";
import { toDdMmYyyy } from "../../../utils/TimeUtils";
import { PersonData } from "../../../services/Schemas";
import { DataContextValue, JamData } from "../../../contexts/DataContext";
import { findItemById } from "../../../utils/Utils";

export interface TableColumn extends ViewField {
	label: string;
	sortable?: boolean;
	searchable?: boolean;
	type?: string;
	sortField?: string | ((item: JamData, dataContext: DataContextValue) => string | number | null);
	searchFields?: string | ((item: JamData, dataContext: DataContextValue) => string | null);
}

const getCompanyText = (item: JamData, context: DataContextValue): string | null => {
	if ("company_id" in item && item.company_id) {
		return findItemById(context.companies, item.company_id)?.name ?? null;
	}
	return null;
};

const getLocationText = (item: JamData, context: DataContextValue): string | null => {
	if ("location_id" in item && item.location_id) {
		const location = findItemById(context.locations, item.location_id);
		if (location) {
			return location.name + item.attendance_type;
		}
	}
	return null;
};

const getJobText = (item: JamData, context: DataContextValue): string | null => {
	if ("job_id" in item) {
		return findItemById(context.jobs, item.job_id)?.name ?? null;
	}
	return null;
};

const _getPersonsText = (item: JamData, context: DataContextValue, key: string): string | null => {
	if (!(key in item)) return null;
	const ids: number = (item as any)[key];
	if (!Array.isArray(ids)) return null;

	const names: string[] = context.persons
		.filter((person: PersonData): boolean => ids.includes(person.id))
		.map((person: PersonData): string => person.name);

	return names.join(" ") || null;
};

const getInterviewersText = (item: JamData, context: DataContextValue): string | null => {
	return _getPersonsText(item, context, "interviewers");
};

interface TableColumnOverrides extends Partial<TableColumn> {}

export const tableColumns = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	idColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "id",
		label: "ID",
		sortable: true,
		searchable: true,
		type: "number",
		...overrides,
	}),

	nameColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "name",
		label: "Name",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	valueColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "value",
		label: "Value",
		sortable: true,
		searchable: true,
		type: "number",
		render: renderFunctions.value,
		...overrides,
	}),

	titleColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "title",
		label: "Title",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	descriptionColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "description",
		label: "Description",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.description,
		...overrides,
	}),

	noteColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "note",
		label: "Notes",
		sortable: false,
		searchable: true,
		type: "text",
		render: renderFunctions.note,
		...overrides,
	}),

	typeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	operatorColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "operator",
		label: "Operator",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	updateTypeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.updateType,
		...overrides,
	}),

	scrapedLocationColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "location",
		label: "Location",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	cityColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "city",
		label: "City",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	postcodeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "postcode",
		label: "Postcode",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	countryColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "country",
		label: "Country",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	scrapedCompanyColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "company",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	personNameColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "name",
		label: "Name",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "last_name",
		...overrides,
	}),

	appThemeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "theme",
		label: "Theme",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.appTheme,
		...overrides,
	}),

	roleColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "role",
		label: "Role",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	daysSinceLastUpdateColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "days_since_last_update",
		label: "Since Last Update",
		sortable: true,
		type: "number",
		render: renderFunctions.lastUpdateDays,
		...overrides,
	}),

	daysUntilDeadlineColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "days_until_deadline",
		label: "Time Until Deadline",
		sortable: true,
		type: "number",
		render: renderFunctions.daysUntilDeadline,
		...overrides,
	}),

	lastUpdateTypeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "last_update_type",
		label: "Last Update",
		sortable: true,
		type: "text",
		...overrides,
	}),

	platformColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "platform",
		label: "Platform",
		sortable: true,
		searchable: true,
		type: "text",
		render: (params: RenderParams) => renderFunctions.capitalise(params, "platform"),
		...overrides,
	}),

	overallScore: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_rating.overall_score",
		label: "AI Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.overallScore,
		...overrides,
	}),

	filterTypeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "type",
		label: "Filter Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.filterType,
		...overrides,
	}),

	filterOperatorColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "operator",
		label: "Operator",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.filterOperator,
		...overrides,
	}),

	// --------------------------------------------------- LINK/EMAIL --------------------------------------------------

	urlColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "url",
		label: "Website",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.url,
		...overrides,
	}),

	urlGenericColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "url",
		label: "Link",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.urlGeneric,
		...overrides,
	}),

	emailColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "email",
		label: "Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.email,
		...overrides,
	}),

	linkedinUrlColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "linkedin_url",
		label: "LinkedIn",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.linkedinUrl,
		...overrides,
	}),

	// ---------------------------------------------------- DATETIME ---------------------------------------------------

	createdAtColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "created_at",
		label: "Date Added",
		type: "date",
		sortable: true,
		searchable: true,
		searchFields: (item: JamData) => toDdMmYyyy(item.created_at),
		render: (params: RenderParams) => renderFunctions._date(params, "created_at"),
		...overrides,
	}),

	dateColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "date",
		label: "Date",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: (item: JamData) => ("date" in item && item.date ? toDdMmYyyy(item.date) : ""),
		render: (params: RenderParams) => renderFunctions._date(params, "date"),
		...overrides,
	}),

	lastLoginColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "last_login",
		label: "Last Login",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: (item: JamData) => ("last_login" in item && item.last_login ? toDdMmYyyy(item.last_login) : ""),
		render: (params: RenderParams) => renderFunctions._date(params, "last_login"),
		...overrides,
	}),

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	locationBadgeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
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

	companyBadgeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "CompanyBadge",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: getCompanyText,
		searchFields: getCompanyText,
		render: renderFunctions.CompanyBadge,
		...overrides,
	}),

	interviewerBadgesColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "interviewers",
		label: "Interviewers",
		sortable: false,
		searchable: true,
		type: "text",
		searchFields: getInterviewersText,
		render: renderFunctions.InterviewerBadges,
		...overrides,
	}),

	jobBadgeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job",
		label: "Job",
		sortable: true,
		searchable: true,
		searchFields: getJobText,
		sortField: getJobText,
		render: (params: RenderParams) => renderFunctions.jobBadge(params),
		...overrides,
	}),

	// ----------------------------------------------------- OTHERS ----------------------------------------------------

	isAdminColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_admin",
		label: "Admin",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.isAdmin,
		...overrides,
	}),

	toastActiveColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "toast_active",
		label: "TOAST",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.toastActive,
		...overrides,
	}),

	isEnabledColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_enabled",
		label: "Enabled",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.isEnabled,
		...overrides,
	}),

	caseSensitiveColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "case_sensitive",
		label: "Case Sensitive",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.caseSensitive,
		...overrides,
	}),

	phoneColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "phone",
		label: "Phone",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.phone,
		...overrides,
	}),

	salaryRangeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "salary_min",
		label: "Salary",
		sortable: true,
		searchable: false,
		type: "text",
		sortField: "salary_min",
		render: renderFunctions.salaryRange,
		...overrides,
	}),

	personalRatingColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "personal_rating",
		label: "Rating",
		sortable: true,
		type: "number",
		render: renderFunctions.personalRating,
		...overrides,
	}),

	applicationStatusColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "application_status",
		label: "Status",
		sortable: true,
		searchable: true,
		render: renderFunctions.applicationStatus,
		...overrides,
	}),

	// ----------------------------------------------------- COUNTS ----------------------------------------------------

	interviewCountLocationColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "interviews",
		label: "Interviews",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._interviewCount(param, "location_id"),
		...overrides,
	}),

	jobCountCompanyColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "company_id"),
		...overrides,
	}),

	jobCountAggregatorColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "source_id"),
		...overrides,
	}),

	jobCountLocationColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "location_id"),
		...overrides,
	}),

	jobCountKeywordColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "keywords"),
		...overrides,
	}),

	jobApplicationCountAggregatorColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_applications",
		label: "Job Applications",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._jobApplicationCount(param, "application_aggregator_id"),
		...overrides,
	}),

	personCountCompanyColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "persons",
		label: "Individuals",
		sortable: true,
		searchable: false,
		render: (param: RenderParams) => renderFunctions._personCount(param, "company_id"),
		...overrides,
	}),

	filteredJobCountColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "filtered_jobs",
		label: "Filtered Jobs",
		sortable: true,
		searchable: false,
		render: renderFunctions.filteredJobCount,
		...overrides,
	}),
};
