import React, { ReactNode, useEffect, useState } from "react";
import { DataContextValue, JamData, useDataContext } from "../../../contexts/DataContext";
import InterviewsTable from "../../tables/InterviewTable";
import JobApplicationUpdateTable from "../../tables/JobApplicationUpdateTable";
import { THEMES } from "../../../utils/Theme";
import LocationMap from "../../Maps/LocationMap";
import {
	AggregatorData,
	CompanyData,
	EnrichedJobData,
	InterviewData,
	JobApplicationUpdateData,
	JobData,
	KeywordData,
	LocationData,
	PersonData,
} from "../../../services/schemas/DataTables";
import JobsTable from "../../tables/JobTable";
import PersonTable from "../../tables/PersonTable";
import { TableColumn } from "./TableColumns";
import { Accordion } from "./Accordion";
import { formatTimedelta, toDdMmYyyy, toDdMmYyyyHhMm } from "../../../utils/TimeUtils";
import {
	getActiveBadge,
	getAdminIcon,
	getApplicationStatusBadgeClass,
	getTableIcon,
	getToastIcon,
	getTrueFalseBadge,
	getUpdateTypeIcon,
} from "./Icons";
import { capitalise, ensureHttpPrefix } from "../../../utils/StringUtils";
import { findItemByKey } from "../../../utils/Utils";
import {
	applicationStatusOptions,
	appliedViaOptions,
	attendanceTypeOptions,
	interviewTypeOptions,
	scrapingFilterOperatorOptions,
	scrapingFilterTypeOptions,
	SelectOption,
	updateTypeOptions,
} from "../form/FormOptions";
import { scrapedJobApi } from "../../../services/api/Services";
import { useAuth } from "../../../contexts/AuthContext";
import ScrapedJobsTableReadOnly from "../../tables/ScrapedJobTableReadOnly";
import LoadingSpinner from "../../spinner/Spinner";
import {
	AggregatorBadge,
	CompanyBadge,
	InterviewBadge,
	JobApplicationUpdateBadge,
	JobBadge,
	KeywordBadge,
	LocationBadge,
	PersonBadge,
} from "./DataBadge";
import { JobRatingData, ScrapedJobData, ScrapingFilterData } from "../../../services/schemas/Services";
import { Currency } from "../../../services/schemas/Others";

// Parameters passed to the view render functions
export interface RenderParams {
	item: any; // item containing the field to render
	view?: boolean; // true if rendered in a modal, false if in a table
	id: string; // id of the rendered element
	columns?: TableColumn[]; // columns for rendered tables
	helpText?: string; // help text
	dataContext: DataContextValue; // data context
	token: string | null;
}

// Base class for Fields (Table or Modal fields)
export interface ViewField {
	key: string; // key used to access the field to render if no render function is used. Also used for the element id.
	render?: (params: RenderParams) => ReactNode; // render function to use
	columns?: TableColumn[]; // columns for rendered tables
	helpText?: string; // help text
}

function filterByKey<T>(items: T[], key: string, id: number | undefined): T[] {
	return items.filter((item: T): boolean => {
		const value = (item as Record<string, any>)[key];
		if (Array.isArray(value)) {
			return value.some((obj: number) => obj === id);
		}
		return value === id;
	});
}

function getJamData<T extends { id: number }>(jamData: T[], id: number | undefined | null): T | undefined {
	return jamData.find((data: T): boolean => data.id === id);
}

function getJamDataList<T extends { id: number }>(jamData: T[], ids: number[] | null | undefined): T[] {
	if (!ids) return [];
	return jamData.filter((data: T): boolean => ids.includes(data.id));
}

const getScrapingFilterTypeLabel = (scrapingFilter: ScrapingFilterData): string | null => {
	return (
		scrapingFilterTypeOptions.filter((option: SelectOption): boolean => option.value === scrapingFilter.type)[0]
			?.label || null
	);
};

const getScrapingFilterOperatorLabel = (scrapingFilter: ScrapingFilterData): string | null => {
	return (
		scrapingFilterOperatorOptions.filter(
			(option: SelectOption): boolean => option.value === scrapingFilter.operator,
		)[0]?.label || null
	);
};

export const getScrapingFilterName = (scrapingFilter: ScrapingFilterData): string => {
	const type = getScrapingFilterTypeLabel(scrapingFilter);
	const operator = getScrapingFilterOperatorLabel(scrapingFilter);
	return type + " " + operator + ' "' + scrapingFilter.value + '"';
};

export const renderFunctions = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	_longText: (param: RenderParams, key: string): ReactNode => {
		const text: string | undefined | null = param.item?.[key];
		if (text) {
			if (param.view) {
				return <p style={{ whiteSpace: "pre-line" }}>{text}</p>;
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
		const themeKey: string | undefined = param.item?.theme;
		if (themeKey) {
			return findItemByKey(THEMES, themeKey)?.name;
		}
		return null;
	},

	updateType: (param: RenderParams): ReactNode => {
		const updateType: string | null =
			updateTypeOptions.filter((option: SelectOption): boolean => option.value === param.item?.type)[0]?.label ||
			null;
		if (updateType) {
			const icon = getUpdateTypeIcon(updateType);
			return (
				<span>
					{icon && <i className={`${icon} me-1`}></i>}
					{updateType}
				</span>
			);
		}
		return null;
	},

	interviewType: (param: RenderParams): ReactNode => {
		return (
			interviewTypeOptions.filter((option: SelectOption): boolean => option.value === param.item?.type)[0]
				?.label || null
		);
	},

	overallScore: (param: RenderParams): number | null => {
		return param.item?.job_rating?.overall_score;
	},

	filterType: (param: RenderParams): ReactNode => {
		return getScrapingFilterTypeLabel(param.item);
	},

	filterOperator: (param: RenderParams): ReactNode => {
		return getScrapingFilterOperatorLabel(param.item);
	},

	scrapingFilterName: (param: RenderParams): ReactNode => {
		return getScrapingFilterName(param.item);
	},

	// --------------------------------------------------- LINK/EMAIL --------------------------------------------------

	_url: (param: RenderParams, attribute: string, displayText: string | null = null): ReactNode => {
		const url: string | undefined = param.item?.[attribute];
		if (url) {
			const safeUrl: string = ensureHttpPrefix(url);
			const linkText: string = displayText || safeUrl?.slice(8);
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

	_email: (param: RenderParams, key: string): ReactNode => {
		const email: string | undefined = param.item?.[key];
		if (email)
			return (
				<a href={`mailto:${email}`} className="text-decoration-none">
					<i className="bi bi-envelope me-1"></i>
					{email}
				</a>
			);
		return null;
	},

	email: (param: RenderParams): ReactNode => {
		return renderFunctions._email(param, "email");
	},

	contactEmail: (param: RenderParams): ReactNode => {
		return renderFunctions._email(param, "contact_email");
	},

	linkedinUrl: (param: RenderParams): ReactNode => {
		const linkedinUrl: string | undefined = param.item?.linkedin_url;
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
		const date: Date | undefined | null = param.item?.[key];
		if (!date) return null;
		return toDdMmYyyy(date);
	},

	datetime: (param: RenderParams): string | null => {
		const date = param.item?.date ? new Date(param.item.date) : null;
		if (!date) return null;
		return toDdMmYyyyHhMm(date);
	},

	// ----------------------------------------------------- OTHER -----------------------------------------------------

	phone: (param: RenderParams): ReactNode => {
		const phone: string | undefined | null = param.item?.phone;
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
		const isAdmin: boolean = param.item?.is_admin;
		const icon: string = getAdminIcon(isAdmin);
		return <i className={icon}></i>;
	},

	premiumActive: (param: RenderParams): ReactNode => {
		return getTrueFalseBadge(param.item?.premium.is_active);
	},

	isActive: (param: RenderParams): ReactNode => {
		return getTrueFalseBadge(param.item?.is_active);
	},

	isRecruiter: (param: RenderParams): ReactNode => {
		return getTrueFalseBadge(param.item?.is_recruiter);
	},

	caseSensitive: (param: RenderParams): ReactNode => {
		return getTrueFalseBadge(param.item?.case_sensitive);
	},

	salaryRange: (param: RenderParams): string | null => {
		const salary_min: number | undefined | null = param.item?.salary_min;
		const salary_max: number | undefined | null = param.item?.salary_max;
		const salaryCurrency: string | undefined | null =
			param.dataContext.currencies.find((currency: Currency) => currency.code === param.item?.salary_currency)
				?.symbol || "";
		if (!salary_min && !salary_max) {
			return null;
		}
		if (salary_min === salary_max && salary_min) {
			return `${salaryCurrency}${salary_min.toLocaleString()}`;
		}
		if (salary_min && salary_max) {
			return `${salaryCurrency}${salary_min.toLocaleString()} - ${salaryCurrency}${salary_max.toLocaleString()}`;
		}
		if (salary_min) return `From ${salaryCurrency}${salary_min.toLocaleString()}`;
		if (salary_max) return `Up to ${salaryCurrency}${salary_max.toLocaleString()}`;
		return null;
	},

	personalRating: (param: RenderParams): ReactNode => {
		const personal_rating: number | undefined | null = param.item?.personal_rating;
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
		const status: string | null =
			applicationStatusOptions.filter(
				(option: SelectOption): boolean => option.value === param.item?.application_status,
			)[0]?.label || null;
		if (status) {
			return <span className={`badge ${getApplicationStatusBadgeClass(status)} badge`}>{status}</span>;
		}
	},

	locationMap: (param: RenderParams): ReactNode => {
		const location: LocationData = param.item;
		const locations: LocationData[] = location ? [location] : [];
		return <LocationMap locations={locations} />;
	},

	scrapedLocationMap: (param: RenderParams): ReactNode => {
		return <LocationMap locations={[param.item]} scrollWheelZoom={false} />;
	},

	lastUpdateDays: (params: RenderParams): ReactNode => {
		const daysSinceLastUpdate: number | undefined | null = params.item?.days_since_last_update;
		return <span className={"text-danger"}>{daysSinceLastUpdate} days</span>;
	},

	daysUntilDeadline: (param: RenderParams): ReactNode => {
		const seconds: number | undefined | null = param.item?.days_until_deadline;
		if (seconds) {
			return <span className={"text-danger"}>{formatTimedelta(seconds)}</span>;
		}
	},

	capitalise: (param: RenderParams, key: string): ReactNode => {
		const text: string | undefined | null = param.item?.[key];
		if (text) {
			return capitalise(text);
		}
		return null;
	},

	jobRating: (param: RenderParams): ReactNode => {
		const job_rating: JobRatingData | undefined | null = param.item?.job_rating;
		if (!job_rating) return null;

		return (
			<div className="card shadow-sm">
				<div className="card-body p-3">
					<table className="table table-sm table-striped table-hover mb-2">
						<thead className="table-light">
							<tr>
								<th className="text-center">Overall</th>
								<th className="text-center">Educational</th>
								<th className="text-center">Experience</th>
								<th className="text-center">Interest</th>
								<th className="text-center">Technical</th>
							</tr>
						</thead>
						<tbody>
							<tr>
								<td className="text-center fw-semibold">{job_rating.overall_score}</td>
								<td className="text-center">{job_rating.educational_score}</td>
								<td className="text-center">{job_rating.experience_score}</td>
								<td className="text-center">{job_rating.interest_score}</td>
								<td className="text-center">{job_rating.technical_score}</td>
							</tr>
						</tbody>
					</table>

					{job_rating.feedback && <div className="small">{job_rating.feedback}</div>}
				</div>
			</div>
		);
	},

	// ----------------------------------------------------- COUNTS ----------------------------------------------------

	_interviewCount: (param: RenderParams, key: keyof InterviewData): number => {
		const ctx: DataContextValue = param.dataContext;
		return filterByKey(ctx.interviews, key, param.item?.id).length;
	},

	_jobCount: (param: RenderParams, key: keyof JobData): number => {
		const ctx: DataContextValue = param.dataContext;
		return filterByKey(ctx.jobs, key, param.item?.id).length;
	},

	_jobApplicationCount: (param: RenderParams, key: keyof JobData): number => {
		const ctx: DataContextValue = param.dataContext;
		return filterByKey(ctx.jobs, key, param.item?.id).length;
	},

	_personCount: (param: RenderParams, key: keyof PersonData): number => {
		const ctx: DataContextValue = param.dataContext;
		return filterByKey(ctx.persons, key, param.item?.id).length;
	},

	filteredJobCount: (param: RenderParams): number => {
		return param.item?.filtered_jobs?.length || 0;
	},

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	jobBadge: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const job: EnrichedJobData | undefined = getJamData(ctx.jobs, param.item?.job_id);

		if (job) {
			return <JobBadge item={job} badgeId={param.id} />;
		}
	},

	interviewBadge: (param: RenderParams): ReactNode => {
		if (param.item) {
			const ctx: DataContextValue = param.dataContext;
			const job: EnrichedJobData | undefined = getJamData(ctx.jobs, param.item.job_id);
			if (job) {
				return <InterviewBadge item={param.item} badgeId={param.id} displayText={job.name} />;
			}
		}
	},

	jobApplicationUpdateBadge: (param: RenderParams): ReactNode => {
		if (param.item) {
			const ctx: DataContextValue = param.dataContext;
			const job: EnrichedJobData | undefined = getJamData(ctx.jobs, param.item.job_id);
			if (job) {
				return <JobApplicationUpdateBadge item={param.item} badgeId={param.id} displayText={job.name} />;
			}
		}
	},

	LocationBadge: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const location: LocationData | undefined = getJamData(ctx.locations, param.item?.location_id);
		const attendanceType: string | null = param.item?.attendance_type;

		let icon: string;
		if (attendanceType === "on-site") {
			icon = "building";
		} else if (attendanceType === "hybrid") {
			icon = "house-door";
		} else {
			icon = "house";
		}

		let attendanceString: string | null =
			attendanceTypeOptions.filter((option: SelectOption): boolean => option.value === attendanceType)[0]
				?.label || null;

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
			return <LocationBadge item={location} badgeId={param.id} icon={icon} displayText={displayText} />;
		} else {
			return null;
		}
	},

	CompanyBadge: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const company: CompanyData | undefined = getJamData(ctx.companies, param.item?.company_id);

		if (company) {
			return <CompanyBadge item={company} badgeId={param.id} />;
		}
		return null;
	},

	_aggregatorBadge: (param: RenderParams, idKey: keyof JobData | keyof ScrapedJobData): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const aggregator: AggregatorData | undefined = getJamData(ctx.aggregators, param.item?.[idKey]);

		if (aggregator) {
			return <AggregatorBadge item={aggregator} badgeId={param.id} />;
		}
		return null;
	},

	AppliedViaBadge: (param: RenderParams): ReactNode => {
		const appliedVia: string | null = param.item?.applied_via;
		const applicationAggregatorId: string | null = param.item?.application_aggregator_id;
		if (appliedVia === "aggregator" && applicationAggregatorId) {
			return renderFunctions._aggregatorBadge(param, "application_aggregator_id");
		}
		if (appliedVia) {
			const text: string =
				appliedViaOptions.filter((option: SelectOption): boolean => option.value === appliedVia)[0]?.label ||
				appliedVia;
			return (
				<span className={"badge bg-info"} id={param.id}>
					{text}
				</span>
			);
		}
		return null;
	},

	SourceBadge: (param: RenderParams): ReactNode => {
		return renderFunctions._aggregatorBadge(param, "source_id");
	},

	KeywordBadges: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const keywords: KeywordData[] = getJamDataList(ctx.keywords, param.item?.keywords);

		if (keywords.length > 0) {
			return (
				<div className="badge-group">
					{keywords.map((keyword, index) => (
						<span key={keyword.id || index} className="me-1">
							<KeywordBadge item={keyword} badgeId={`${param.id}-${index}`} />
						</span>
					))}
				</div>
			);
		}
		return null;
	},

	_personBadges: (param: RenderParams, key: string, parent: JamData): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const persons: PersonData[] = getJamDataList(ctx.persons, param.item?.[key]);

		if (persons.length > 0) {
			return (
				<div className="badge-group">
					{persons.map((person: PersonData, index: number) => (
						<span key={person.id || index} className="me-1">
							<PersonBadge item={person} badgeId={`${param.id}-${index}`} parentItem={parent} />
						</span>
					))}
				</div>
			);
		}
		return null;
	},

	ContactBadges: (param: RenderParams): ReactNode => {
		return renderFunctions._personBadges(param, "contacts", param.item);
	},

	InterviewerBadges: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const job: EnrichedJobData = getJamData(ctx.jobs, param.item?.job_id)!;
		return renderFunctions._personBadges(param, "interviewers", job);
	},

	// ----------------------------------------------------- TABLES ----------------------------------------------------

	InterviewTable: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const interviews: InterviewData[] = filterByKey(ctx.interviews, "job_id", param.item?.id);
		return <InterviewsTable data={interviews} jobId={param.item?.id} />;
	},

	JobApplicationUpdateTable: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const updates: JobApplicationUpdateData[] = filterByKey(ctx.jobApplicationUpdates, "job_id", param.item?.id);
		return <JobApplicationUpdateTable data={updates} jobId={param.item?.id} />;
	},

	// ------------------------------------------------ ACCORDION TABLES -----------------------------------------------

	_accordionJobTable: (param: RenderParams, key: string): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const jobs: EnrichedJobData[] = filterByKey(ctx.jobs, key, param.item?.id);
		return (
			<Accordion title="Jobs" data={jobs} icon={getTableIcon("Jobs")} helpText={param.helpText}>
				{(data: EnrichedJobData[]) => <JobsTable data={data} columns={param.columns} />}
			</Accordion>
		);
	},

	AccordionInterviewTable: (param: RenderParams, key: string): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const interviews: InterviewData[] = filterByKey(ctx.interviews, key, param.item?.id);
		return (
			<Accordion title="Interviews" data={interviews} icon={getTableIcon("Interviews")} helpText={param.helpText}>
				{(data: InterviewData[]) => <InterviewsTable data={data} showAdd={false} columns={param.columns} />}
			</Accordion>
		);
	},

	accordionJobApplicationTable: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const jobs: EnrichedJobData[] = filterByKey(ctx.jobs, "application_aggregator_id", param.item?.id);
		return (
			<Accordion
				title="Job Applications"
				data={jobs}
				icon={getTableIcon("Job Applications")}
				helpText={param.helpText}
			>
				{(data: EnrichedJobData[]) => <JobsTable data={data} columns={param.columns} />}
			</Accordion>
		);
	},

	AccordionPersonTable: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const persons: PersonData[] = filterByKey(ctx.persons, "company_id", param.item?.id);
		return (
			<Accordion title="Persons" data={persons} icon={getTableIcon("Persons")} helpText={param.helpText}>
				{(data: PersonData[]) => <PersonTable data={data} columns={param.columns} />}
			</Accordion>
		);
	},

	accordionScrapedJobTable: (param: RenderParams) => <AccordionScrapedJobTable param={param} />,
};

export const RenderViewFieldWithContext: React.FC<{
	field: ViewField;
	item: any;
	id: string;
}> = ({ field, item, id }) => {
	const context: DataContextValue = useDataContext();
	const { token } = useAuth();

	let rendered: ReactNode;
	if (field.render) {
		const renderParams: RenderParams = {
			item: item,
			view: false,
			id: `${id}-${field.key}`,
			columns: field.columns,
			helpText: field.helpText,
			dataContext: context,
			token: token,
		};
		rendered = field.render(renderParams);
	} else {
		rendered = item?.[field.key];
	}

	if (rendered !== null && rendered !== undefined && rendered !== "") {
		return <>{rendered}</>;
	} else {
		return <span className="text-muted">Not Provided</span>;
	}
};

const AccordionScrapedJobTable: React.FC<{ param: RenderParams }> = ({ param }) => {
	const [data, setData] = useState<ScrapedJobData[] | null>(null);
	const [loading, setLoading] = useState<boolean>(true);

	useEffect(() => {
		const fetchData = async (): Promise<void> => {
			if (!param.token || !param.item.id) return;
			setLoading(true);
			try {
				const response = await scrapedJobApi.getByFilterId(param.item.id, param.token);
				setData(response.data);
			} catch (error) {
				console.error("Error fetching filtered scraped jobs:", error);
				setData([]);
			} finally {
				setLoading(false);
			}
		};

		fetchData().then();
	}, [param.item.id, param.token]);

	if (loading) {
		return <LoadingSpinner size={"sm"} />;
	}

	if (!data) {
		return null;
	}

	return (
		<Accordion
			title="Filtered Jobs"
			data={data}
			icon={getTableIcon("Scraped Jobs")}
			helpText="Scraped Jobs that were filtered by this filter."
		>
			{(rows: ScrapedJobData[]) => <ScrapedJobsTableReadOnly data={rows} columns={param.columns} />}
		</Accordion>
	);
};
