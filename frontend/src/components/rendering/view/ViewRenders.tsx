import React, { ReactNode } from "react";
import InterviewsTable from "../../tables/InterviewTable";
import JobApplicationUpdateTable from "../../tables/JobApplicationUpdateTable";
import { THEMES } from "../../../utils/Theme";
import LocationMap from "../../maps/LocationMap";
import {
	AggregatorOut,
	CompanyOut,
	InterviewData,
	JobData,
	KeywordOut,
	LocationData,
	PersonData,
	PersonOut,
} from "../../../services/Schemas";
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

export interface RenderParams {
	item: any;
	view?: boolean;
	id?: string;
	columns?: TableColumn[];
	helpText?: string;
	onChange?: () => void;
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

const ensureHttpPrefix = (url: string): string => {
	if (url.match(/^https?:\/\//)) return url;
	return `https://${url}`;
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
		const locations: LocationData[] = param.item ? [param.item] : [];
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
		const interviews = param.item?.interviews;
		return interviews?.length || 0;
	},

	jobCount: (param: RenderParams): number => {
		const jobs = param.item?.jobs;
		return jobs?.length || 0;
	},

	jobApplicationCount: (param: RenderParams): number => {
		const jobs = param.item?.job_applications;
		return jobs?.length || 0;
	},

	personCount: (param: RenderParams): number => {
		const persons = param.item?.persons;
		return persons?.length || 0;
	},

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	_jobBadge: (param: RenderParams, attribute: string, displayAttribute: keyof JobData): ReactNode => {
		const job: JobData = param.item?.[attribute];
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
		return renderFunctions._jobBadge(param, "job", "title");
	},

	jobNameBadge: (param: RenderParams): ReactNode => {
		return renderFunctions._jobBadge(param, "job", "name");
	},

	keywordBadges: (param: RenderParams): ReactNode => {
		const keywords: KeywordOut[] = param.item?.keywords;
		if (keywords?.length > 0) {
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
		const location: LocationData = param.item?.location;
		const attendanceType = param.item?.attendance_type;

		if (attendanceType === "remote") {
			return (
				<span className="badge bg-warning" id={param.id}>
					<i className="bi bi-house me-1"></i>
					Remote
				</span>
			);
		}

		if (location) {
			let displayText = location.name;
			let icon = "bi-building";
			if (attendanceType === "on-site") {
				displayText = `${location.name} (On-site)`;
			} else if (attendanceType === "hybrid") {
				displayText = `${location.name} (Hybrid)`;
			} else {
				displayText = `${location.name} (Remote)`;
				icon = "bi-house";
			}

			return (
				<LocationModalManager>
					{(handleClick) => (
						<span
							className="badge bg-warning clickable-badge"
							onClick={() => handleClick(location.id)}
							id={param.id}
						>
							<i className={`bi ${icon} me-1`}></i>
							{displayText}
						</span>
					)}
				</LocationModalManager>
			);
		}

		if (attendanceType && attendanceType !== "remote") {
			return (
				<span className="badge bg-warning" id={param.id}>
					<i className="bi bi-building me-1"></i>
					{attendanceType.charAt(0).toUpperCase() + attendanceType.slice(1)}
				</span>
			);
		}

		return null;
	},

	companyBadge: (param: RenderParams): ReactNode => {
		const company: CompanyOut = param.item?.company;
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
		const persons: PersonOut[] = param.item?.[key];
		if (persons?.length > 0) {
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
			return renderFunctions._aggregatorBadge(param, "application_aggregator");
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

	_aggregatorBadge: (param: RenderParams, attribute: string): ReactNode => {
		const aggregator: AggregatorOut = param.item?.[attribute];
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
		return renderFunctions._aggregatorBadge(param, "source");
	},

	// ----------------------------------------------------- TABLES ----------------------------------------------------

	interviewTable: (param: RenderParams): ReactNode => {
		const interviews = param.item?.interviews;
		return <InterviewsTable data={interviews} jobId={param.item?.id} onDataChange={param.onChange} />;
	},

	jobApplicationUpdateTable: (param: RenderParams): ReactNode => {
		const updates = param.item?.updates;
		return <JobApplicationUpdateTable data={updates} jobId={param.item?.id} onDataChange={param.onChange} />;
	},

	// ------------------------------------------------ ACCORDION TABLES -----------------------------------------------

	accordionJobTable: (param: RenderParams): ReactNode => {
		const jobs: JobData[] = param.item?.jobs;
		return (
			<Accordion title="Jobs" data={jobs} icon={getTableIcon("Jobs")} helpText={param.helpText}>
				{(data) => <JobsTable onDataChange={param.onChange} data={data} columns={param.columns} />}
			</Accordion>
		);
	},

	accordionInterviewTable: (param: RenderParams): ReactNode => {
		const interviews: InterviewData[] = param.item?.interviews;
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
		const jobs: JobData[] = param.item?.job_applications;
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
		const persons: PersonData[] = param.item?.persons;
		return (
			<Accordion title="Persons" data={persons} icon={getTableIcon("Persons")} helpText={param.helpText}>
				{(data) => <PersonTable data={data} onDataChange={param.onChange} columns={param.columns} />}
			</Accordion>
		);
	},
};

export const renderViewField = (field: ViewField, item: any, id: string, onChange?: any): ReactNode => {
	let rendered: ReactNode;
	if (field.render) {
		const renderParams: RenderParams = {
			item: item,
			view: false,
			id: `${id}-${field.key}`,
			columns: field.columns,
			helpText: field.helpText,
			onChange: onChange,
		};
		rendered = field.render(renderParams);
	} else {
		rendered = item?.[field.key];
	}

	if (rendered !== null && rendered !== undefined) {
		// allow for 0
		return rendered;
	} else {
		return <span className="text-muted">Not Provided</span>;
	}
};
