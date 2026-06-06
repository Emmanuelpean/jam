import { ReactNode } from "react";
import {
	getInterviewCount,
	getJobApplicationUpdateCount,
	getTotalInterviewCount,
	getTotalJobApplicationUpdateCount,
	renderFunctions,
	RenderParams,
	ViewField,
} from "./ViewRenders";
import { toDdMmYyyy } from "../../../utils/TimeUtils";
import { DataContextValue, JamData } from "../../../contexts/DataContext";
import { findItemById } from "../../../utils/Utils";
import { AggregatorData, CompanyData, EnrichedJobData, JobData, KeywordData, PersonData } from "../../../services/schemas/DataTables";
import { FilterConfig } from "../../DataTable/FilterTypes";
import {
	applicationStatusOptions,
	attendanceTypeOptions,
	interviewTypeOptions,
	updateTypeOptions,
} from "../form/FormOptions";

export interface TableColumn<T extends JamData = JamData> extends ViewField {
	label: string;
	sortable?: boolean;
	searchable?: boolean;
	type?: string;
	minWidth?: string;
	sortField?: string | ((item: T, dataContext: DataContextValue) => string | number | null);
	searchFields?: string | ((item: T, dataContext: DataContextValue) => string | null);
	filterConfig?: FilterConfig;
	sidebarExtra?: ReactNode;

	_entityType?(item: T): void; // phantom — method shorthand gives bivariance needed for structural checks
}

const getCompanyText = (item: { company_id: number | null }, context: DataContextValue): string | null => {
	if (item.company_id) {
		return findItemById(context.companies, item.company_id)?.name ?? null;
	}
	return null;
};

const getLocationText = (item: { location: string | null; attendance_type: string | null }): string | null => {
	if (item.location) {
		return item.location + (item.attendance_type || "");
	}
	return null;
};

const getJobText = (item: { job_id: number }, context: DataContextValue): string | null => {
	return findItemById(context.jobs, item.job_id)?.name ?? null;
};

const getSourceAggregatorText = (
	item: { source_aggregator_id: number | null },
	context: DataContextValue
): string | null => {
	if (item.source_aggregator_id) {
		return findItemById(context.aggregators, item.source_aggregator_id)?.name ?? null;
	}
	return null;
};

const getPersonsText = (ids: number[], context: DataContextValue): string | null => {
	const names: string[] = context.persons
		.filter((person: PersonData): boolean => ids.includes(person.id))
		.map((person: PersonData): string => person.name);
	return names.join(" ") || null;
};

const getInterviewersText = (item: { interviewers: number[] }, context: DataContextValue): string | null =>
	getPersonsText(item.interviewers, context);

const getContactsText = (item: { contacts: number[] }, context: DataContextValue): string | null =>
	getPersonsText(item.contacts, context);

const getRecruiterText = (item: { recruiter_id: number | null }, context: DataContextValue): string | null => {
	if (!item.recruiter_id) return null;
	return context.persons.find((p: PersonData): boolean => p.id === item.recruiter_id)?.name ?? null;
};

function maxCount<T>(items: T[], countFn: (item: T) => number): number {
	if (items.length === 0) return 1;
	return Math.max(1, ...items.map(countFn));
}

type ColumnOverrides<T extends JamData = JamData> = Omit<Partial<TableColumn<T>>, "_entityType">;

export const tableColumns = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	idColumn: <T extends JamData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "id",
		label: "ID",
		sortable: true,
		searchable: true,
		type: "number",
		...overrides,
	}),

	nameColumn: <T extends JamData & { name: string | null }>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "name",
		label: "Name",
		sortable: true,
		searchable: true,
		type: "text",
		filterConfig: { type: "text" },
		...overrides,
	}),

	valueColumn: <T extends JamData & { value: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "value",
		label: "Value",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.value,
		filterConfig: { type: "text" },
		...overrides,
	}),

	titleColumn: <T extends JamData & { title: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "title",
		label: "Title",
		sortable: true,
		searchable: true,
		type: "text",
		filterConfig: { type: "text" },
		...overrides,
	}),

	subjectColumn: <T extends JamData & { subject: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "subject",
		label: "Subject",
		sortable: true,
		searchable: true,
		type: "text",
		filterConfig: { type: "text" },
		...overrides,
	}),

	descriptionColumn: <T extends JamData & { description?: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	noteColumn: <T extends JamData & { note: string | null }>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
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

	interviewTypeColumn: <T extends JamData & { type: string }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.interviewType,
		filterConfig: { type: "select", options: interviewTypeOptions },
		...overrides,
	}),

	updateTypeColumn: <T extends JamData & { type: string }>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "type",
		label: "Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.updateType,
		filterConfig: { type: "select", options: updateTypeOptions },
		...overrides,
	}),

	scrapedCompanyColumn: <T extends JamData & { company: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "company",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		...overrides,
	}),

	personNameColumn: <T extends JamData & { name: string; last_name: string }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "name",
		label: "Name",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "last_name",
		filterConfig: { type: "text" },
		...overrides,
	}),

	roleColumn: <T extends JamData & { role: string | null }>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "role",
		label: "Role",
		sortable: true,
		searchable: true,
		type: "text",
		filterConfig: { type: "text" },
		...overrides,
	}),

	daysSinceLastUpdateColumn: <T extends JamData & { days_since_last_update: number | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "days_since_last_update",
		label: "Since Last Update",
		sortable: true,
		type: "number",
		render: renderFunctions.lastUpdateDays,
		...overrides,
	}),

	daysUntilDeadlineColumn: <T extends JamData & { days_until_deadline: number | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "days_until_deadline",
		label: "Time Until Deadline",
		sortable: true,
		type: "number",
		render: renderFunctions.daysUntilDeadline,
		...overrides,
	}),

	lastUpdateTypeColumn: <T extends JamData & { last_update_type: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "last_update_type",
		label: "Last Update",
		sortable: true,
		type: "text",
		...overrides,
	}),

	isImportedColumn: <T extends JamData & { is_imported: boolean }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "is_imported",
		label: "Imported",
		sortable: true,
		searchable: false,
		type: "boolean",
		render: renderFunctions.isImported,
		...overrides,
	}),

	isActiveColumn: <T extends JamData & { is_active: boolean }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "is_active",
		label: "Active",
		sortable: true,
		searchable: true,
		type: "boolean",
		render: renderFunctions.isActive,
		...overrides,
	}),

	platformColumn: <T extends JamData & { platform: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "platform",
		label: "Platform",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.platform,
		filterConfig: { type: "text" },
		...overrides,
	}),

	overallScore: <T extends JamData & { job_rating: { overall_score: number | null } | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "job_rating.overall_score",
		label: "AI Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.overallScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	technicalScoreColumn: <T extends JamData & { job_rating: { technical_score: number | null } | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "job_rating.technical_score",
		label: "Technical Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.technicalScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	experienceScoreColumn: <T extends JamData & { job_rating: { experience_score: number | null } | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "job_rating.experience_score",
		label: "Experience Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.experienceScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	educationalScoreColumn: <T extends JamData & { job_rating: { educational_score: number | null } | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "job_rating.educational_score",
		label: "Education Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.educationalScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	interestScoreColumn: <T extends JamData & { job_rating: { interest_score: number | null } | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "job_rating.interest_score",
		label: "Interest Score",
		sortable: true,
		searchable: false,
		type: "number",
		render: renderFunctions.interestScore,
		filterConfig: { type: "number", min: 0, max: 10, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	filterTypeColumn: <T extends JamData & { type: string }>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "type",
		label: "Filter Type",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.filterType,
		...overrides,
	}),

	filterOperatorColumn: <T extends JamData & { operator: string }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "operator",
		label: "Operator",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.filterOperator,
		...overrides,
	}),

	attendanceTypeColumn: <T extends JamData & { attendance_type: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	urlColumn: <T extends JamData & { url: string | null }>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "url",
		label: "Website",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.url,
		filterConfig: { type: "text" },
		...overrides,
	}),

	urlGenericColumn: <T extends JamData & { url: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "url",
		label: "Link",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.urlGeneric,
		filterConfig: { type: "text" },
		...overrides,
	}),

	emailColumn: <T extends JamData & { email: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "email",
		label: "Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.email,
		filterConfig: { type: "text" },
		...overrides,
	}),

	contactEmailColumn: <T extends JamData & { contact_email: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "contact_email",
		label: "Contact Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.contactEmail,
		...overrides,
	}),

	linkedinUrlColumn: <T extends JamData & { linkedin_url: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	createdAtColumn: <T extends JamData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "created_at",
		label: "Date Added",
		type: "date",
		sortable: true,
		searchable: true,
		searchFields: (item) => toDdMmYyyy(item.created_at),
		render: (params: RenderParams) => renderFunctions._date(params, "created_at"),
		filterConfig: { type: "date" },
		...overrides,
	}),

	dateColumn: <T extends JamData & { date: Date | null | undefined }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "date",
		label: "Date",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: (item) => (item.date ? toDdMmYyyy(item.date) : ""),
		render: (params: RenderParams) => renderFunctions._date(params, "date"),
		filterConfig: { type: "date" },
		...overrides,
	}),

	lastLoginColumn: <T extends JamData & { last_login: Date | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "last_login",
		label: "Last Login",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: (item) => (item.last_login ? toDdMmYyyy(item.last_login) : null),
		render: (params: RenderParams) => renderFunctions._date(params, "last_login"),
		...overrides,
	}),

	applicationDeadline: <T extends JamData & { deadline: Date | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "deadline",
		label: "Deadline",
		sortable: true,
		searchable: true,
		type: "date",
		searchFields: (item) => (item.deadline ? toDdMmYyyy(item.deadline) : ""),
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

	locationBadgeColumn: <T extends JamData & { location: string | null; attendance_type: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	companyBadgeColumn: <T extends JamData & { company_id: number | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	interviewerBadgesColumn: <T extends JamData & { interviewers: number[] }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	contactBadgesColumn: <T extends JamData & { contacts: number[] }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	jobBadgeColumn: <T extends JamData & { job_id: number }>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "jobBadge",
		label: "Job",
		sortable: true,
		searchable: true,
		searchFields: getJobText,
		sortField: getJobText,
		render: (params: RenderParams): ReactNode => renderFunctions.jobBadge(params),
		filterConfig: { type: "reference", entityKey: "jobs", valueField: "job_id", labelKey: "title" },
		...overrides,
	}),

	sourceAggregatorBadgeColumn: <T extends JamData & { source_aggregator_id: number | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "sourceAggregatorBadge",
		label: "Source Aggregator",
		sortable: true,
		searchable: true,
		searchFields: getSourceAggregatorText,
		sortField: getSourceAggregatorText,
		render: (params: RenderParams): ReactNode => renderFunctions._aggregatorBadge(params, "source_aggregator_id"),
		filterConfig: { type: "reference", entityKey: "aggregators", valueField: "source_aggregator_id" },
		...overrides,
	}),

	sourceContactBadgeColumn: <T extends JamData & { recruiter_id: number | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "sourceContactBadge",
		label: "Source Contact",
		sortable: true,
		searchable: true,
		searchFields: getRecruiterText,
		render: (params: RenderParams): ReactNode => renderFunctions._personBadge(params, "recruiter_id"),
		filterConfig: { type: "reference", entityKey: "persons", valueField: "recruiter_id" },
		...overrides,
	}),

	KeywordBadgeColumn: <T extends JamData & { keywords: number[]; source_aggregator_id: number | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "keywords",
		label: "Tags",
		sortable: false,
		searchable: true,
		searchFields: getSourceAggregatorText,
		render: renderFunctions.KeywordBadges,
		filterConfig: { type: "reference", entityKey: "keywords", valueField: "keywords" },
		...overrides,
	}),

	// ----------------------------------------------------- OTHERS ----------------------------------------------------

	isAdminColumn: <T extends JamData & { is_admin: boolean }>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "is_admin",
		label: "Admin",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.isAdmin,
		...overrides,
	}),

	isRecruiterColumn: <T extends JamData & { is_recruiter: boolean }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "is_recruiter",
		label: "Recruiter",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.isRecruiter,
		...overrides,
	}),

	toastActiveColumn: <T extends JamData & { premium: { is_active: boolean } }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "premium_active",
		label: "Premium",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.premiumActive,
		sortField: (item): number => (item.premium.is_active ? 1 : 0),
		...overrides,
	}),

	caseSensitiveColumn: <T extends JamData & { case_sensitive: boolean }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "case_sensitive",
		label: "Case Sensitive",
		sortable: true,
		searchable: false,
		type: "text",
		render: renderFunctions.caseSensitive,
		...overrides,
	}),

	phoneColumn: <T extends JamData & { phone: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "phone",
		label: "Phone",
		sortable: true,
		searchable: true,
		type: "text",
		render: renderFunctions.phone,
		filterConfig: { type: "text" },
		...overrides,
	}),

	salaryRangeColumn: <T extends JamData & { salary_min: number | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	personalRatingColumn: <T extends JamData & { personal_rating: number | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "personal_rating",
		label: "Rating",
		sortable: true,
		type: "number",
		render: renderFunctions.personalRating,
		filterConfig: { type: "number", min: 0, max: 5, step: 1, display: "slider", nullable: true },
		...overrides,
	}),

	isFavouriteColumn: <T extends JamData & { is_favourite: boolean }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	applicationStatusColumn: <T extends JamData & { application_status: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "application_status",
		label: "Status",
		sortable: true,
		searchable: true,
		render: renderFunctions.applicationStatus,
		filterConfig: { type: "select", options: applicationStatusOptions },
		...overrides,
	}),

	// ----------------------------------------------------- COUNTS ----------------------------------------------------

	jobCountCompanyColumn: <T extends CompanyData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: T, ctx: DataContextValue): number =>
			ctx.jobs.filter((j: JobData): boolean => j.company_id === item.id).length,
		render: (param: RenderParams): number => renderFunctions._jobCount(param, "company_id"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue): number =>
				maxCount(
					ctx.companies,
					(c: CompanyData): number => ctx.jobs.filter((j: JobData): boolean => j.company_id === c.id).length
				),
		},
		...overrides,
	}),

	jobCountAggregatorColumn: <T extends AggregatorData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: T, ctx: DataContextValue): number =>
			ctx.jobs.filter((j: JobData): boolean => j.source_aggregator_id === item.id).length,
		render: (param: RenderParams): number => renderFunctions._jobCount(param, "source_aggregator_id"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue): number =>
				maxCount(
					ctx.aggregators,
					(a: AggregatorData): number =>
						ctx.jobs.filter((j: JobData): boolean => j.source_aggregator_id === a.id).length
				),
		},
		...overrides,
	}),

	jobCountKeywordColumn: <T extends KeywordData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "jobs",
		label: "Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: T, ctx: DataContextValue): number =>
			ctx.jobs.filter((j: JobData): boolean => Array.isArray(j.keywords) && j.keywords.includes(item.id)).length,
		render: (param: RenderParams): number => renderFunctions._jobCount(param, "keywords"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue): number =>
				maxCount(
					ctx.keywords,
					(k: KeywordData): number =>
						ctx.jobs.filter((j: JobData): boolean => Array.isArray(j.keywords) && j.keywords.includes(k.id))
							.length
				),
		},
		...overrides,
	}),

	jobApplicationCountAggregatorColumn: <T extends AggregatorData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "job_applications",
		label: "Job Applications",
		sortable: true,
		searchable: false,
		sortField: (item: T, ctx: DataContextValue): number =>
			ctx.jobs.filter((j: JobData): boolean => j.application_aggregator_id === item.id).length,
		render: (param: RenderParams): number =>
			renderFunctions._jobApplicationCount(param, "application_aggregator_id"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue): number =>
				maxCount(
					ctx.aggregators,
					(a: AggregatorData): number =>
						ctx.jobs.filter((j: JobData): boolean => j.application_aggregator_id === a.id).length
				),
		},
		...overrides,
	}),

	personCountCompanyColumn: <T extends CompanyData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "persons",
		label: "Individuals",
		sortable: true,
		searchable: false,
		sortField: (item: T, ctx: DataContextValue): number =>
			ctx.persons.filter((p: PersonData): boolean => p.company_id === item.id).length,
		render: (param: RenderParams): number => renderFunctions._personCount(param, "company_id"),
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: (ctx: DataContextValue): number =>
				maxCount(
					ctx.companies,
					(c: CompanyData): number =>
						ctx.persons.filter((p: PersonData): boolean => p.company_id === c.id).length
				),
		},
		...overrides,
	}),

	recruitedJobCountCompanyColumn: <T extends CompanyData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "recruiter_jobs",
		label: "Submitted Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: T, ctx: DataContextValue): number =>
			ctx.jobs.filter((p: JobData): boolean => p.recruitment_company_id === item.id).length,
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
						ctx.jobs.filter((p: JobData): boolean => p.recruitment_company_id === c.id).length
				),
		},
		...overrides,
	}),

	filteredJobCountColumn: <T extends JamData & { filtered_jobs: number[] }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "filtered_jobs",
		label: "Filtered Jobs",
		sortable: true,
		searchable: false,
		sortField: (item: T): number => item.filtered_jobs.length,
		render: renderFunctions.filteredJobCount,
		filterConfig: { type: "number", min: 0, max: 50, step: 1, display: "slider" },
		...overrides,
	}),

	interviewCountColumn: <T extends EnrichedJobData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "interviews",
		label: "Interviews",
		sortable: true,
		searchable: false,
		sortField: getInterviewCount,
		render: renderFunctions.interviewCount,
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: getTotalInterviewCount,
		},
		...overrides,
	}),

	jobApplicationUpdateCountColumn: <T extends EnrichedJobData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "updates",
		label: "Updates",
		sortable: true,
		searchable: false,
		sortField: getJobApplicationUpdateCount,
		render: renderFunctions.jobApplicationUpdateCount,
		filterConfig: {
			type: "number",
			min: 0,
			step: 1,
			display: "slider",
			max: getTotalJobApplicationUpdateCount,
		},
		...overrides,
	}),

	scrapingStatusColumn: <T extends JamData & { is_processed: boolean }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "is_processed",
		label: "Status",
		sortable: true,
		searchable: false,
		render: renderFunctions.scrapingStatus,
		...overrides,
	}),

	expiredReasonColumn: <T extends JamData & { is_closed: boolean; deadline: Date | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
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

	alertNameColumn: <T extends JamData & { alert_name: string | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "alert_name",
		label: "Alert Name",
		sortable: true,
		searchable: true,
		type: "text",
		filterConfig: { type: "text" },
		...overrides,
	}),

	jobsFoundColumn: <T extends JamData & { job_found_n: number }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "job_found_n",
		label: "Jobs Found",
		sortable: true,
		type: "number",
		filterConfig: { type: "number", min: 0, max: 100, step: 1, display: "slider" },
		...overrides,
	}),

	dateReceivedColumn: <T extends JamData & { date_received: Date | null }>(
		overrides: ColumnOverrides<T> = {}
	): TableColumn<T> => ({
		key: "date_received",
		label: "Date Received",
		sortable: true,
		type: "date",
		searchFields: (item) => (item.date_received ? toDdMmYyyy(item.date_received) : ""),
		render: (params: RenderParams) => renderFunctions._date(params, "date_received"),
		filterConfig: { type: "date" },
		...overrides,
	}),

	// ---------------------------------------------------- FILE COLUMNS --------------------------------------------------

	filenameColumn: <T extends JamData & { filename: string }>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "filename",
		label: "Filename",
		sortable: true,
		searchable: true,
		type: "text",
		filterConfig: { type: "text" },
		...overrides,
	}),

	fileUsagesColumn: <T extends JamData>(overrides: ColumnOverrides<T> = {}): TableColumn<T> => ({
		key: "fileUsages",
		label: "Used in",
		sortable: true,
		searchable: false,
		sortField: (item, ctx) => ctx.jobs.filter((j) => j.cv_id === item.id || j.cover_letter_id === item.id).length,
		render: (params: RenderParams) => renderFunctions.fileUsages(params),
		...overrides,
	}),
};
