import React, { ReactNode } from "react";
import { useDataContext } from "../../../contexts/DataContext";
import InterviewsTable from "../../tables/InterviewTable";
import JobApplicationUpdateTable from "../../tables/JobApplicationUpdateTable";
import { THEMES } from "../../../utils/Theme";
import LocationMap from "../../maps/LocationMap";
import { InterviewData, JobData, LocationData, PersonData } from "../../../services/Schemas";
import JobsTable from "../../tables/JobTable";
import PersonTable from "../../tables/PersonTable";
import { TableColumn } from "./TableColumns";
import { Accordion } from "./Accordion";
import {
	AggregatorModalManager,
	CompanyModalManager,
	JobModalManager,
	KeywordModalManager,
	LocationModalManager,
	PersonModalManager,
} from "../../modals/ModalManagers";
import { formatTimedelta } from "../../../utils/TimeUtils";

type ContextData = {
	companies: any[];
	locations: any[];
	aggregators: any[];
	persons: any[];
	keywords: any[];
	jobs: any[];
	interviews: any[];
	jobApplicationUpdates: any[];
};

export interface RenderParams {
	item: any;
	view?: boolean;
	id?: string;
	columns?: TableColumn[];
	helpText?: string;
	onChange?: () => void;
	contextData?: ContextData;
}

// Base class for Fields (Table or Modal fields)
export interface ViewField {
	key: string;
	render?: (params: RenderParams) => ReactNode;
	columns?: TableColumn[];
	helpText?: string;
}

export const getApplicationStatusBadgeClass = (status: string | undefined): string => {
	switch (status?.toLowerCase()) {
		case "applied":
			return "bg-primary";
		case "interview":
			return "bg-warning";
		case "offer":
			return "bg-success";
		case "rejected":
		case "withdrawn":
			return "bg-secondary";
		default:
			return "bg-primary";
	}
};

function getUpdateTypeIcon(type: string): string {
	switch (type?.toLowerCase()) {
		case "received":
			return "bi-download";
		default:
			return "bi-upload";
	}
}

export function getTableIcon(title: string): string {
	const iconMap: Record<string, string> = {
		Jobs: "bi-briefcase",
		Companies: "bi-building",
		Persons: "bi-people",
		People: "bi-people",
		Locations: "bi-geo-alt",
		Tags: "bi-tags",
		Interviews: "bi-calendar-event",
		"Job Applications": "bi-person-workspace",
		"Job Application Updates": "bi-bell",
		"Job Aggregators": "bi-linkedin",
		Users: "bi-person-lines-fill",
		Settings: "bi-database-gear",
	};
	return iconMap[title] || "bi-table";
}

export const getAdminIcon = (isAdmin: boolean): string => {
	if (isAdmin) {
		return "bi bi-person-check text-success";
	} else {
		return "bi bi-person-x text-danger";
	}
};

export const getToastIcon = (toastActive: boolean): string => {
	if (toastActive) {
		return "bi bi-cup-hot text-success";
	} else {
		return "bi bi-cup text-danger";
	}
};

const ensureHttpPrefix = (url: string): string => {
	if (url.match(/^https?:\/\//)) return url;
	return `https://${url}`;
};

const getIds = (param: RenderParams, key: string) => {
	return (param.item?.[key] || []).map((p: { id: number }): number => p.id);
};

function filterByKey(items: any[], key: string, id: number | undefined): any[] {
	return items.filter((item) => {
		const value = item[key];
		if (Array.isArray(value)) {
			// value is an array of objects with an id property
			return value.some((obj: { id: number }) => obj.id === id);
		}
		// value is a number
		return value === id;
	});
}

const lookupEntity = {
	getCompany: (companies: any[], id: number | null | undefined) => (id ? companies.find((c) => c.id === id) : null),

	getLocation: (locations: any[], id: number | null | undefined) => (id ? locations.find((l) => l.id === id) : null),

	getAggregator: (aggregators: any[], id: number | null | undefined) =>
		id ? aggregators.find((a) => a.id === id) : null,

	getPerson: (persons: any[], id: number | null | undefined) => (id ? persons.find((p) => p.id === id) : null),

	getKeyword: (keywords: any[], id: number | null | undefined) => (id ? keywords.find((k) => k.id === id) : null),

	getJob: (jobs: any[], id: number | null | undefined) => (id ? jobs.find((j) => j.id === id) : null),

	getPersons: (persons: any[], ids: number[] | null | undefined) =>
		ids ? persons.filter((p) => ids.includes(p.id)) : [],

	getKeywords: (keywords: any[], ids: number[] | null | undefined) =>
		ids ? keywords.filter((k) => ids.includes(k.id)) : [],

	getInterviews: (interviews: any[], ids: number[] | null | undefined) =>
		ids ? interviews.filter((i) => ids.includes(i.id)) : [],

	getJobApplicationUpdates: (updates: any[], ids: number[] | null | undefined) =>
		ids ? updates.filter((u) => ids.includes(u.id)) : [],

	getJobs: (jobs: any[], ids: number[] | null | undefined) => (ids ? jobs.filter((j) => ids.includes(j.id)) : []),
};

export const renderFunctions = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	_longText: (param: RenderParams, key: string): ReactNode => {
		const text = param.item?.[key];
		if (text) {
			if (param.view) {
				return text;
			} else {
				const words = text.split(" ");
				const truncated = words.slice(0, 12).join(" ");
				const needsEllipsis = words.length > 12;

				return (
					<div style={{ overflow: "hidden", textOverflow: "ellipsis" }}>
						{truncated}
						{needsEllipsis ? "..." : ""}
					</div>
				);
			}
		}
		return null;
	},

	note: (param: RenderParams): ReactNode => {
		return renderFunctions._longText(param, "note");
	},

	applicationNote: (param: RenderParams): ReactNode => {
		return renderFunctions._longText(param, "application_note");
	},

	description: (param: RenderParams): ReactNode => {
		return renderFunctions._longText(param, "description");
	},

	value: (param: RenderParams): ReactNode => {
		return renderFunctions._longText(param, "value");
	},

	appTheme: (param: RenderParams): ReactNode => {
		const themeKey = param.item?.theme;
		if (themeKey) {
			const theme = THEMES.find((theme) => theme.key === themeKey);
			return theme?.name;
		}
		return null;
	},

	updateType: (param: RenderParams): ReactNode => {
		const updateType = param.item?.type;
		if (updateType) {
			const capitalizedType = updateType.charAt(0).toUpperCase() + updateType.slice(1);
			const icon = getUpdateTypeIcon(updateType);

			return (
				<span>
					{icon && <i className={`${icon} me-1`}></i>}
					{capitalizedType}
				</span>
			);
		}
		return null;
	},

	// --------------------------------------------------- LINK/EMAIL --------------------------------------------------

	_url: (param: RenderParams, attribute: string, displayText: string | null = null): ReactNode => {
		const url = param.item?.[attribute];
		if (url) {
			const safeUrl = ensureHttpPrefix(url);
			const linkText = displayText || safeUrl?.slice(8);
			return (
				<a href={safeUrl} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					{linkText} <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
		return null;
	},

	url: (param: RenderParams): ReactNode => {
		return renderFunctions._url(param, "url");
	},

	urlGeneric: (param: RenderParams): ReactNode => {
		return renderFunctions._url(param, "url", "Link");
	},

	applicationUrl: (param: RenderParams): ReactNode => {
		return renderFunctions._url(param, "application_url");
	},

	email: (param: RenderParams): ReactNode => {
		const email = param.item?.email;
		if (email)
			return (
				<a href={`mailto:${email}`} className="text-decoration-none">
					<i className="bi bi-envelope me-1"></i>
					{email}
				</a>
			);
		return null;
	},

	linkedinUrl: (param: RenderParams): ReactNode => {
		const linkedinUrl = param.item?.linkedin_url;
		if (linkedinUrl) {
			return (
				<a href={linkedinUrl} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					<i className="bi bi-linkedin me-1"></i>
					Profile <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
		return null;
	},

	// ---------------------------------------------------- DATETIME ---------------------------------------------------

	_date: (param: RenderParams, key: string): string | null => {
		const date = param.item?.[key];
		if (date) {
			return new Date(date).toLocaleDateString();
		}
		return null;
	},

	lastLogin: (param: RenderParams): string | null => {
		return renderFunctions._date(param, "last_login");
	},

	createdDate: (param: RenderParams): string | null => {
		return renderFunctions._date(param, "created_at");
	},

	applicationDate: (param: RenderParams): string | null => {
		return renderFunctions._date(param, "application_date");
	},

	deadline: (param: RenderParams): string | null => {
		return renderFunctions._date(param, "deadline");
	},

	date: (param: RenderParams): string | null => {
		return renderFunctions._date(param, "date");
	},

	datetime: (param: RenderParams): string | null => {
		const date = param.item?.date;
		if (date) {
			return (
				new Date(date).toLocaleDateString() +
				" " +
				new Date(date).toLocaleTimeString([], {
					hour: "2-digit",
					minute: "2-digit",
				})
			);
		}
		return null;
	},

	followupSnoozeDateTime: (param: RenderParams): string | null => {
		return renderFunctions._date(param, "followup_snooze_datetime");
	},

	// ----------------------------------------------------- OTHER -----------------------------------------------------

	phone: (param: RenderParams): ReactNode => {
		const phone = param.item?.phone;
		if (phone) {
			return (
				<a href={`tel:${phone}`} className="text-decoration-none">
					<i className="bi bi-telephone me-1"></i>
					{phone}
				</a>
			);
		}
		return null;
	},

	isAdmin: (param: RenderParams): ReactNode => {
		const isAdmin = param.item?.is_admin;
		const icon = getAdminIcon(isAdmin);
		return <i className={icon}></i>;
	},

	toastActive: (param: RenderParams): ReactNode => {
		const toastActive = param.item?.toast_active;
		const icon = getToastIcon(toastActive);
		return <i className={icon}></i>;
	},

	isActive: (param: RenderParams): ReactNode => {
		const isActive = param.item?.is_active;
		if (isActive) {
			return <span className="badge bg-success">Active</span>;
		} else {
			return <span className="badge bg-secondary">Inactive</span>;
		}
	},

	salaryRange: (param: RenderParams): string | null => {
		const salary_min = param.item?.salary_min;
		const salary_max = param.item?.salary_max;
		if (!salary_min && !salary_max) {
			return null;
		}
		if (salary_min === salary_max) {
			return `£${salary_min.toLocaleString()}`;
		}
		if (salary_min && salary_max) {
			return `£${salary_min.toLocaleString()} - £${salary_max.toLocaleString()}`;
		}
		if (salary_min) return `From £${salary_min.toLocaleString()}`;
		if (salary_max) return `Up to £${salary_max.toLocaleString()}`;
		return null;
	},

	personalRating: (param: RenderParams): ReactNode => {
		const personal_rating = param.item?.personal_rating;
		if (personal_rating) {
			const rating = Math.max(0, Math.min(5, personal_rating));

			return (
				<div className="star-rating-container" style={{ height: "auto" }}>
					{[...Array(5)].map((_, index) => {
						const starNumber = index + 1;
						const starClass = starNumber <= rating ? "bi-star-fill" : "bi-star";

						return (
							<i
								key={starNumber}
								className={`star-rating-star ${starClass}`}
								style={{ fontSize: "1rem", cursor: "auto" }}
							/>
						);
					})}
				</div>
			);
		}
		return null;
	},

	applicationStatus: (param: RenderParams): ReactNode => {
		const status = param.item?.application_status;
		if (status) {
			return <span className={`badge ${getApplicationStatusBadgeClass(status)} badge`}>{status}</span>;
		}
	},

	locationMap: (param: RenderParams): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;
		const location = lookupEntity.getLocation(ctx.locations, param.item?.location_id);
		const locations: LocationData[] = location ? [location] : [];
		return <LocationMap locations={locations} />;
	},

	lastUpdateDays: (params: RenderParams): ReactNode => {
		const daysSinceLastUpdate = params.item?.days_since_last_update;
		return <span className={"text-danger"}>{daysSinceLastUpdate} days</span>;
	},

	daysUntilDeadline: (param: RenderParams): ReactNode => {
		const seconds = param.item?.days_until_deadline;
		if (typeof seconds === "number") {
			return <span className={"text-danger"}>{formatTimedelta(seconds)}</span>;
		}
	},

	// ----------------------------------------------------- COUNTS ----------------------------------------------------

	interviewCount: (param: RenderParams): number => {
		const ctx = param.contextData;
		if (!ctx) return 0;

		const interviewIds = getIds(param, "interviews");
		const interviews = lookupEntity.getInterviews(ctx.interviews, interviewIds);
		return interviews.length;
	},

	_jobCount: (param: RenderParams, key: string): number => {
		const ctx = param.contextData;
		if (!ctx) return 0;
		return filterByKey(ctx.jobs, key, param.item?.id).length;
	},

	jobApplicationCountAggregator: (param: RenderParams): number => {
		const ctx = param.contextData;
		if (!ctx) return 0;
		return filterByKey(ctx.jobs, "application_aggregator_id", param.item?.id).length;
	},

	personCountCompany: (param: RenderParams): number => {
		const ctx = param.contextData;
		if (!ctx) return 0;
		return filterByKey(ctx.persons, "company_id", param.item?.id).length;
	},

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	_jobBadge: (param: RenderParams, idKey: string, displayAttribute: keyof JobData): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;

		const jobId = param.item?.[idKey];
		const job = lookupEntity.getJob(ctx.jobs, jobId);

		if (job) {
			return (
				<JobModalManager>
					{(handleClick) => (
						<span
							className={`badge bg-info clickable-badge`}
							onClick={() => handleClick(job.id)}
							id={param.id}
						>
							<i className="bi bi-briefcase me-1"></i>
							{String(job[displayAttribute])}
						</span>
					)}
				</JobModalManager>
			);
		}
		return null;
	},

	jobBadge: (param: RenderParams): ReactNode => {
		return renderFunctions._jobBadge(param, "job_id", "title");
	},

	jobNameBadge: (param: RenderParams): ReactNode => {
		return renderFunctions._jobBadge(param, "job_id", "name");
	},

	keywordBadges: (param: RenderParams): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;

		const keywordIds = (param.item?.keywords || []).map((p: { id: number }): number => p.id);
		const keywords = lookupEntity.getKeywords(ctx.keywords, keywordIds);

		if (keywords.length > 0) {
			return (
				<div className="badge-group">
					{keywords.map((keyword, index) => (
						<span key={keyword.id || index} className="me-1">
							<KeywordModalManager>
								{(handleClick) => (
									<span
										className="badge bg-info clickable-badge"
										onClick={() => handleClick(keyword.id)}
										id={param.id ? `${param.id}-${index}` : undefined}
									>
										<i className="bi bi-tag me-1"></i>
										{keyword.name}
									</span>
								)}
							</KeywordModalManager>
						</span>
					))}
				</div>
			);
		}
		return null;
	},

	locationBadge: (param: RenderParams): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;

		const location = lookupEntity.getLocation(ctx.locations, param.item?.location_id);
		const attendanceType = param.item?.attendance_type;

		let icon: string;
		if (attendanceType === "on-site") {
			icon = "bi-building";
		} else if (attendanceType === "hybrid") {
			icon = "bi-house-door";
		} else {
			icon = "bi-house";
		}

		let attendanceString: string | null = null;
		if (attendanceType === "on-site") {
			attendanceString = "On-site";
		} else if (attendanceType === "hybrid") {
			attendanceString = "Hybrid";
		} else if (attendanceType === "remote") {
			attendanceString = "Remote";
		}

		let displayText: string | null = null;
		if (location && attendanceString) {
			displayText = `${location.name} (${attendanceString})`;
		} else if (location) {
			displayText = location.name;
		} else if (attendanceString) {
			displayText = attendanceString;
		} else {
			return null;
		}

		if (displayText) {
			return (
				<LocationModalManager>
					{(handleClick) => (
						<span
							className="badge bg-warning clickable-badge"
							onClick={() => location && handleClick(location.id)}
							id={param.id}
						>
							<i className={`bi ${icon} me-1`}></i>
							{displayText}
						</span>
					)}
				</LocationModalManager>
			);
		} else {
			return null;
		}
	},

	companyBadge: (param: RenderParams): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;

		const company = lookupEntity.getCompany(ctx.companies, param.item?.company_id);

		if (company) {
			return (
				<CompanyModalManager>
					{(handleClick) => (
						<span
							className={"badge bg-info clickable-badge"}
							onClick={() => handleClick(company.id)}
							id={param.id}
						>
							<i className="bi bi-building me-1"></i>
							{company.name}
						</span>
					)}
				</CompanyModalManager>
			);
		}
		return null;
	},

	_personBadges: (param: RenderParams, key: string): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;

		const personIds = getIds(param, key);
		const persons = lookupEntity.getPersons(ctx.persons, personIds);

		if (persons.length > 0) {
			return (
				<div className="badge-group">
					{persons.map((person, index) => (
						<span key={person.id || index} className="me-1">
							<PersonModalManager>
								{(handleClick) => (
									<span
										className="badge bg-info clickable-badge"
										onClick={() => handleClick(person.id)}
										id={param.id ? `${param.id}-${index}` : undefined}
									>
										<i className="bi bi-file-person me-1"></i>
										{person.name}
									</span>
								)}
							</PersonModalManager>
						</span>
					))}
				</div>
			);
		}
		return null;
	},

	contactBadges: (param: RenderParams): ReactNode => {
		return renderFunctions._personBadges(param, "contacts");
	},

	interviewerBadges: (param: RenderParams): ReactNode => {
		return renderFunctions._personBadges(param, "interviewers");
	},

	appliedViaBadge: (param: RenderParams): ReactNode => {
		const appliedVia = param.item?.applied_via;
		if (appliedVia === "aggregator") {
			return renderFunctions._aggregatorBadge(param, "application_aggregator_id");
		}
		if (appliedVia) {
			return (
				<span className={"badge bg-info"} id={param.id}>
					{appliedVia}
				</span>
			);
		}
		return null;
	},

	_aggregatorBadge: (param: RenderParams, idKey: string): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;

		const aggregator = lookupEntity.getAggregator(ctx.aggregators, param.item?.[idKey]);

		if (aggregator) {
			return (
				<AggregatorModalManager>
					{(handleClick) => (
						<span
							className={"badge bg-info clickable-badge"}
							onClick={() => handleClick(aggregator.id)}
							id={param.id}
						>
							<i className="bi bi-building me-1"></i>
							{aggregator.name}
						</span>
					)}
				</AggregatorModalManager>
			);
		}
		return null;
	},

	sourceBadge: (param: RenderParams): ReactNode => {
		return renderFunctions._aggregatorBadge(param, "source_id");
	},

	// ----------------------------------------------------- TABLES ----------------------------------------------------

	interviewTable: (param: RenderParams): ReactNode => {
		const ctx: ContextData | undefined = param.contextData;
		if (!ctx) return null;
		const interviews = lookupEntity.getInterviews(ctx.interviews, param.item.id);
		return <InterviewsTable data={interviews} jobId={param.item?.id} onDataChange={param.onChange} />;
	},

	jobApplicationUpdateTable: (param: RenderParams): ReactNode => {
		const ctx: ContextData | undefined = param.contextData;
		if (!ctx) return null;
		const updates = lookupEntity.getJobApplicationUpdates(ctx.jobApplicationUpdates, param.item?.id);
		return <JobApplicationUpdateTable data={updates} jobId={param.item?.id} onDataChange={param.onChange} />;
	},

	// ------------------------------------------------ ACCORDION TABLES -----------------------------------------------

	_accordionJobTable: (param: RenderParams, key: string): ReactNode => {
		const ctx: ContextData | undefined = param.contextData;
		if (!ctx) return null;

		const jobs = filterByKey(ctx.jobs, key, param.item?.id);
		return (
			<Accordion title="Jobs" data={jobs} icon={getTableIcon("Jobs")} helpText={param.helpText}>
				{(data) => <JobsTable onDataChange={param.onChange} data={data} columns={param.columns} />}
			</Accordion>
		);
	},

	accordionInterviewTable: (param: RenderParams, key: string): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;

		const interviews = filterByKey(ctx.interviews, key, param.item?.id);
		return (
			<Accordion title="Interviews" data={interviews} icon={getTableIcon("Interviews")} helpText={param.helpText}>
				{(data) => (
					<InterviewsTable
						data={data}
						onDataChange={param.onChange}
						showAdd={false}
						columns={param.columns}
					/>
				)}
			</Accordion>
		);
	},

	accordionJobApplicationTable: (param: RenderParams): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;

		const jobs = filterByKey(ctx.jobs, "application_aggregator_id", param.item?.id);
		return (
			<Accordion
				title="Job Applications"
				data={jobs}
				icon={getTableIcon("Job Applications")}
				helpText={param.helpText}
			>
				{(data) => <JobsTable data={data} onDataChange={param.onChange} columns={param.columns} />}
			</Accordion>
		);
	},

	accordionPersonTable: (param: RenderParams): ReactNode => {
		const ctx = param.contextData;
		if (!ctx) return null;

		const persons = filterByKey(ctx.persons, "company_id", param.item?.id);
		return (
			<Accordion title="Persons" data={persons} icon={getTableIcon("Persons")} helpText={param.helpText}>
				{(data) => <PersonTable data={data} onDataChange={param.onChange} columns={param.columns} />}
			</Accordion>
		);
	},
};

export const RenderViewFieldWithContext: React.FC<{
	field: ViewField;
	item: any;
	id: string;
	onChange?: any;
}> = ({ field, item, id, onChange }) => {
	const context = useDataContext();

	let rendered: ReactNode;
	if (field.render) {
		const renderParams: RenderParams = {
			item: item,
			view: false,
			id: `${id}-${field.key}`,
			columns: field.columns,
			helpText: field.helpText,
			onChange: onChange,
			contextData: {
				companies: context.companies,
				locations: context.locations,
				aggregators: context.aggregators,
				persons: context.persons,
				keywords: context.keywords,
				jobs: context.jobs,
				interviews: context.interviews,
				jobApplicationUpdates: context.jobApplicationUpdates,
			},
		};
		rendered = field.render(renderParams);
	} else {
		rendered = item?.[field.key];
	}

	if (rendered !== null && rendered !== undefined) {
		return <>{rendered}</>;
	} else {
		return <span className="text-muted">Not Provided</span>;
	}
};
