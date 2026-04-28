import { ReactNode } from "react";
import { renderFunctions, RenderParams, ViewField } from "./ViewRenders";
import { toDdMmYyyy } from "../../../utils/TimeUtils";
import { DataContextValue, JamData } from "../../../contexts/DataContext";
import { findItemById } from "../../../utils/Utils";
import { CompanyData, EnrichedJobData, PersonData } from "../../../services/schemas/DataTables";
import { FilterConfig } from "../../DataTable/FilterTypes";
import {
	applicationStatusOptions,
	attendanceTypeOptions,
	interviewTypeOptions,
	updateTypeOptions,
} from "../form/FormOptions";

export interface TableColumn extends ViewField {
	label: string;
	sortable?: boolean;
	searchable?: boolean;
	type?: string;
	minWidth?: string;
	sortField?: string | ((item: JamData, dataContext: DataContextValue) => string | number | null);
	searchFields?: string | ((item: JamData, dataContext: DataContextValue) => string | null);
	filterConfig?: FilterConfig;
	sidebarExtra?: ReactNode;
}

const getCompanyText = (item: JamData, context: DataContextValue): string | null => {
	if ("company_id" in item && item.company_id) {
		return findItemById(context.companies, item.company_id)?.name ?? null;
	}
	return null;
};

const getLocationText = (item: JamData): string | null => {
	if ("location" in item && item.location) {
		return (item.location as string) + ((item as any).attendance_type || "");
	}
	return null;
};

const getJobText = (item: JamData, context: DataContextValue): string | null => {
	if ("job_id" in item) {
		return findItemById(context.jobs, item.job_id)?.name ?? null;
	}
	return null;
};

const getSourceAggregatorText = (item: JamData, context: DataContextValue): string | null => {
	if ("source_aggregator_id" in item && item.source_aggregator_id) {
		return findItemById(context.aggregators, item.source_aggregator_id)?.name ?? null;
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

const getContactsText = (item: JamData, context: DataContextValue): string | null => {
	return _getPersonsText(item, context, "contacts");
};

function maxCount<T>(items: T[], countFn: (item: T) => number): number {
	if (items.length === 0) return 1;
	return Math.max(1, ...items.map(countFn));
}

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
		filterConfig: { type: "text" },
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
		filterConfig: { type: "text" },
		...overrides,
	}),

	descriptionColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "description",
		label: "Description",
		sortable: true,
		searchable: true,
		type: "text",
		minWidth: "200px",
		render: renderFunctions.description,
		filterConfig: { type: "text" },
		...overrides,
	}),

	noteColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "note",
		label: "Notes",
		sortable: true,
		searchable: true,
		type: "text",
		minWidth: "150px",
		render: renderFunctions.note,
		filterConfig: { type: "text" },
		...overrides,
	}),

	interviewTypeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.interviewType,
		filterConfig: { type: "select", options: interviewTypeOptions },
		...overrides,
	}),

	updateTypeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.updateType,
		filterConfig: { type: "select", options: updateTypeOptions },
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
		filterConfig: { type: "text" },
		...overrides,
	}),

	roleColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "role",
		label: "Role",
		sortable: true,
		searchable: true,
		type: "text",
		filterConfig: { type: "text" },
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

	isImportedColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_imported",
		label: "Imported",
		sortable: true,
		searchable: false,
		type: "boolean",
		render: renderFunctions.isImported,
		...overrides,
	}),

	isActiveColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_active",
		label: "Active",
		sortable: true,
		searchable: true,
		type: "boolean",
		render: renderFunctions.isActive,
		...overrides,
	}),

	platformColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "platform",
		label: "Platform",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.platform,
		filterConfig: { type: "text" },
		...overrides,
	}),

	overallScore: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_rating.overall_score",
		label: "AI Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.overallScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	technicalScoreColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_rating.technical_score",
		label: "Technical Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.technicalScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	experienceScoreColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_rating.experience_score",
		label: "Experience Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.experienceScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	educationalScoreColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_rating.educational_score",
		label: "Education Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.educationalScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	interestScoreColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_rating.interest_score",
		label: "Interest Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.interestScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
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

	attendanceTypeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "attendance_type",
		label: "Attendance Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.attendanceType,
		filterConfig: { type: "select", options: attendanceTypeOptions },
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
		filterConfig: { type: "text" },
		...overrides,
	}),

	urlGenericColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "url",
		label: "Link",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.urlGeneric,
		filterConfig: { type: "text" },
		...overrides,
	}),

	emailColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "email",
		label: "Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.email,
		filterConfig: { type: "text" },
		...overrides,
	}),

	contactEmailColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "contact_email",
		label: "Contact Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.contactEmail,
		...overrides,
	}),

	linkedinUrlColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "linkedin_url",
		label: "LinkedIn",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.linkedinUrl,
		filterConfig: { type: "text" },
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
		filterConfig: { type: "date" },
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
		filterConfig: { type: "date" },
		...overrides,
	}),

	lastLoginColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "last_login",
		label: "Last Login",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: (item: JamData) => ("last_login" in item && item.last_login ? toDdMmYyyy(item.last_login) : null),
		render: (params: RenderParams) => renderFunctions._date(params, "last_login"),
		...overrides,
	}),

	applicationDeadline: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "deadline",
		label: "Deadline",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: (item: JamData) => ("deadline" in item && item.deadline ? toDdMmYyyy(item.deadline) : ""),
		render: (params: RenderParams) => renderFunctions._date(params, "deadline"),
		filterConfig: {
			type: "date",
			presets: [
				{ key: "pastDeadline", label: "Past deadline" },
				{ key: "next7", label: "Next 7 days" },
				{ key: "next30", label: "Next 30 days" },
				{ key: "thisMonth", label: "This month" },
				{ key: "custom", label: "Custom" },
			],
		},
		...overrides,
	}),

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	locationBadgeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "locationBadge",
		label: "Location",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: getLocationText,
		searchFields: getLocationText,
		render: (params: RenderParams): ReactNode => renderFunctions.locationBadge(params),
		filterConfig: { type: "text" },
		...overrides,
	}),

	companyBadgeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "companyBadge",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: getCompanyText,
		searchFields: getCompanyText,
		render: renderFunctions.CompanyBadge,
		filterConfig: { type: "reference", entityKey: "companies", valueField: "company_id" },
		...overrides,
	}),

	interviewerBadgesColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "interviewerBadges",
		label: "Interviewers",
		sortable: false,
		searchable: true,
		type: "text",
		searchFields: getInterviewersText,
		render: renderFunctions.InterviewerBadges,
		filterConfig: { type: "reference", entityKey: "persons", valueField: "interviewers" },
		...overrides,
	}),

	contactBadgesColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "contactBadges",
		label: "Contacts",
		sortable: false,
		searchable: true,
		type: "text",
		searchFields: getContactsText,
		render: renderFunctions.ContactBadges,
		filterConfig: { type: "reference", entityKey: "persons", valueField: "contacts" },
		...overrides,
	}),

	jobBadgeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobBadge",
		label: "Job",
		sortable: true,
		searchable: true,
		searchFields: getJobText,
		sortField: getJobText,
		render: (params: RenderParams) => renderFunctions.jobBadge(params),
		filterConfig: { type: "reference", entityKey: "jobs", valueField: "job_id", labelKey: "title" },
		...overrides,
	}),

	sourceAggregatorBadgeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "sourceAggregatorBadge",
		label: "Source Aggregator",
		sortable: true,
		searchable: true,
		searchFields: getSourceAggregatorText,
		sortField: getSourceAggregatorText,
		render: (params: RenderParams) => renderFunctions._aggregatorBadge(params, "source_aggregator_id"),
		filterConfig: { type: "reference", entityKey: "aggregators", valueField: "source_aggregator_id" },
		...overrides,
	}),

	sourceContactBadgeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "sourceContactBadge",
		label: "Source Contact",
		sortable: true,
		searchable: true,
		searchFields: (item: JamData, dataContext: DataContextValue) =>
			_getPersonsText(item, dataContext, "recruiter_id"),
		render: (params: RenderParams) => renderFunctions._personBadge(params, "recruiter_id"),
		filterConfig: { type: "reference", entityKey: "persons", valueField: "recruiter_id" },
		...overrides,
	}),

	KeywordBadgeColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "keywords",
		label: "Tags",
		sortable: false,
		searchable: true,
		// searchFields: (item: JamData, dataContext: DataContextValue) => getSourceAggregatorText(),
		render: renderFunctions.KeywordBadges,
		filterConfig: { type: "reference", entityKey: "keywords", valueField: "keywords" },
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

	isRecruiterColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_recruiter",
		label: "Recruiter",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.isRecruiter,
		...overrides,
	}),

	toastActiveColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "premium_active",
		label: "Premium",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.premiumActive,
		...overrides,
	}),

	isEnabledColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_enabled",
		label: "Active",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.isActive,
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
		filterConfig: { type: "text" },
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
		filterConfig: { type: "number", min: 0, max: 200000, step: 1000, display: "input" },
		...overrides,
	}),

	personalRatingColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "personal_rating",
		label: "Rating",
		sortable: true,
		type: "number",
		render: renderFunctions.personalRating,
		filterConfig: { type: "number", min: 0, max: 5, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	isFavouriteColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_favourite",
		label: "Favourite",
		sortable: true,
		render: renderFunctions.isFavourite,
		filterConfig: {
			type: "select",
			options: [
				{ value: "true", label: "Yes" },
				{ value: "false", label: "No" },
			],
		},
		...overrides,
	}),

	applicationStatusColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "application_status",
		label: "Status",
		sortable: true,
		searchable: true,
		render: renderFunctions.applicationStatus,
		filterConfig: { type: "select", options: applicationStatusOptions },
		...overrides,
	}),

	// ----------------------------------------------------- COUNTS ----------------------------------------------------

	jobCountCompanyColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: JamData, ctx: DataContextValue) =>
			ctx.jobs.filter((j: any) => j.company_id === item.id).length,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "company_id"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue) =>
				maxCount(ctx.companies, (c) => ctx.jobs.filter((j: any) => j.company_id === c.id).length),
		},
		...overrides,
	}),

	jobCountAggregatorColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: JamData, ctx: DataContextValue) =>
			ctx.jobs.filter((j: any) => j.source_aggregator_id === item.id).length,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "source_aggregator_id"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue) =>
				maxCount(ctx.aggregators, (a) => ctx.jobs.filter((j: any) => j.source_aggregator_id === a.id).length),
		},
		...overrides,
	}),

	jobCountKeywordColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: JamData, ctx: DataContextValue) =>
			ctx.jobs.filter((j: any) => Array.isArray(j.keywords) && j.keywords.includes(item.id)).length,
		render: (param: RenderParams) => renderFunctions._jobCount(param, "keywords"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue) =>
				maxCount(
					ctx.keywords,
					(k) => ctx.jobs.filter((j: any) => Array.isArray(j.keywords) && j.keywords.includes(k.id)).length
				),
		},
		...overrides,
	}),

	jobApplicationCountAggregatorColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_applications",
		label: "Job Applications",
		sortable: true,
		searchable: false,
		sortField: (item: JamData, ctx: DataContextValue) =>
			ctx.jobs.filter((j: any) => j.application_aggregator_id === item.id).length,
		render: (param: RenderParams) => renderFunctions._jobApplicationCount(param, "application_aggregator_id"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue) =>
				maxCount(
					ctx.aggregators,
					(a) => ctx.jobs.filter((j: any) => j.application_aggregator_id === a.id).length
				),
		},
		...overrides,
	}),

	personCountCompanyColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "persons",
		label: "Individuals",
		sortable: true,
		searchable: false,
		sortField: (item: JamData, ctx: DataContextValue) =>
			ctx.persons.filter((p: any) => p.company_id === item.id).length,
		render: (param: RenderParams) => renderFunctions._personCount(param, "company_id"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue) =>
				maxCount(ctx.companies, (c) => ctx.persons.filter((p: any) => p.company_id === c.id).length),
		},
		...overrides,
	}),

	recruitedJobCountCompanyColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "recruiter_jobs",
		label: "Submitted Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: JamData, ctx: DataContextValue): number =>
			ctx.jobs.filter((p: EnrichedJobData): boolean => p.recruitment_company_id === item.id).length,
		render: (param: RenderParams): number => renderFunctions._jobCount(param, "recruitment_company_id"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue): number =>
				maxCount(
					ctx.companies,
					(c: CompanyData): number =>
						ctx.jobs.filter((p: EnrichedJobData): boolean => p.recruitment_company_id === c.id).length
				),
		},
		...overrides,
	}),

	filteredJobCountColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "filtered_jobs",
		label: "Filtered Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: JamData) => (item as any).filtered_jobs?.length || 0,
		render: renderFunctions.filteredJobCount,
		filterConfig: { type: "number", min: 0, max: 50, step: 1, display: "slider" },
		...overrides,
	}),

	interviewCountColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "interviews",
		label: "Interviews",
		sortable: true,
		searchable: false,
		sortField: (item: JamData) => (item as any).interviews?.length || 0,
		render: renderFunctions.interviewCount,
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue) => maxCount(ctx.jobs, (j: any) => j.interviews?.length || 0),
		},
		...overrides,
	}),

	jobApplicationUpdateCountColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "updates",
		label: "Updates",
		sortable: true,
		searchable: false,
		sortField: (item: JamData) => (item as any).updates?.length || 0,
		render: renderFunctions.jobApplicationUpdateCount,
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue) => maxCount(ctx.jobs, (j: any) => j.updates?.length || 0),
		},
		...overrides,
	}),

	scrapingStatusColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_processed",
		label: "Status",
		sortable: true,
		searchable: false,
		render: renderFunctions.scrapingStatus,
		...overrides,
	}),

	expiredReasonColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "is_closed",
		label: "Expired Reason",
		sortable: false,
		searchable: false,
		render: ({ item }: RenderParams) => {
			if (!item) return null;
			const now = new Date();
			if (item.is_closed) return <span className="badge bg-danger">Closed</span>;
			if (item.deadline && new Date(item.deadline) < now)
				return <span className="badge bg-warning text-dark">Past Deadline</span>;
			return null;
		},
		...overrides,
	}),

	// -------------------------------------------------- JOB EMAIL --------------------------------------------------

	alertNameColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "alert_name",
		label: "Alert Name",
		sortable: true,
		searchable: true,
		type: "text",
		filterConfig: { type: "text" },
		...overrides,
	}),

	jobsFoundColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "job_found_n",
		label: "Jobs Found",
		sortable: true,
		type: "number",
		filterConfig: { type: "number", min: 0, max: 100, step: 1, display: "slider" },
		...overrides,
	}),

	dateReceivedColumn: (overrides: TableColumnOverrides = {}): TableColumn => ({
		key: "date_received",
		label: "Date Received",
		sortable: true,
		type: "date",
		searchFields: (item: JamData) =>
			"date_received" in item && item.date_received ? toDdMmYyyy(item.date_received) : "",
		render: (params: RenderParams) => renderFunctions._date(params, "date_received"),
		filterConfig: { type: "date" },
		...overrides,
	}),
};
