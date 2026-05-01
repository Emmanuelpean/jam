import React, { ReactNode, useEffect, useState, JSX } from "react";
import { DataContextValue, JamData, useDataContext } from "../../../contexts/DataContext";
import InterviewsTable from "../../DataTable/InterviewTable";
import JobApplicationUpdateTable from "../../DataTable/JobApplicationUpdateTable";
import LocationMap from "../../Maps/LocationMap";
import {
	AggregatorData,
	CompanyData,
	EnrichedJobData,
	InterviewData,
	JobApplicationUpdateData,
	JobData,
	KeywordData,
	PersonData,
} from "../../../services/schemas/DataTables";
import JobsTable from "../../DataTable/JobTable";
import PersonTable from "../../DataTable/PersonTable";
import { TableColumn } from "./TableColumns";
import { formatTimedelta, toDdMmYyyy, toDdMmYyyyHhMm } from "../../../utils/TimeUtils";
import {
	getAdminIcon,
	getApplicationStatusBadgeClass,
	getLocationIcon,
	getTableIcon,
	getTrueFalseBadge,
	getUpdateTypeIcon,
} from "./Icons";
import { ensureHttpPrefix } from "../../../utils/StringUtils";
import {
	applicationStatusOptions,
	appliedViaOptions,
	attendanceTypeOptions,
	interviewTypeOptions,
	scrapingFilterOperatorOptions,
	scrapingFilterTypeOptions,
	SelectOption,
	sourceTypeOptions,
	updateTypeOptions,
} from "../form/FormOptions";
import { filesApi } from "../../../services/api/DataTables";
import { jobEmailApi, scrapedJobApi } from "../../../services/api/Services";
import { canPreviewFile, formatFileSize } from "../../../utils/FileUtils";
import { useAuth } from "../../../contexts/AuthContext";
import ScrapedJobsTableReadOnly from "../../DataTable/ScrapedJobTableReadOnly";
import JobEmailTableReadOnly from "../../DataTable/JobEmailTableReadOnly";
import LoadingSpinner from "../../Spinner/Spinner";
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
import { JobEmailData, ScrapedJobData, ScrapingFilterData } from "../../../services/schemas/Services";
import JobRatingSection from "./JobRatingSection";
import EmailBody from "./EmailBody";
import { Currency } from "../../../services/schemas/Others";
import { Accordion } from "../../Accordion/Accordion";
import { HelpBubble } from "../../HelpBubble/HelpBubble";
import { Button } from "react-bootstrap";

// Parameters passed to the view render functions
export interface RenderParams {
	item: any; // item containing the field to render
	view?: boolean; // true if rendered in a modal, false if in a table
	id: string; // id of the rendered element
	columns?: TableColumn[]; // columns for rendered tables
	helpText?: string; // help text
	dataContext: DataContextValue; // data context
	token: string | null;
	label?: string;
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
			(option: SelectOption): boolean => option.value === scrapingFilter.operator
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

	htmlBody: (param: RenderParams, key: string): ReactNode => {
		const body: string | undefined | null = (param.item as JobEmailData)?.[key as keyof JobEmailData] as string;
		if (!body) return null;
		const isHtml: boolean = /<[a-z][\s\S]*>/i.test(body);
		return isHtml ? <EmailBody html={body} /> : <p style={{ whiteSpace: "pre-line" }}>{body}</p>;
	},

	value: (param: RenderParams): ReactNode => {
		return renderFunctions._longText(param, "value");
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

	technicalScore: (param: RenderParams): number | null => {
		return param.item?.job_rating?.technical_score;
	},

	experienceScore: (param: RenderParams): number | null => {
		return param.item?.job_rating?.experience_score;
	},

	educationalScore: (param: RenderParams): number | null => {
		return param.item?.job_rating?.educational_score;
	},

	interestScore: (param: RenderParams): number | null => {
		return param.item?.job_rating?.interest_score;
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

	attendanceType: (param: RenderParams): ReactNode => {
		const attendanceType: string | null = param.item.attendance_type;
		return (
			attendanceTypeOptions.filter((option: SelectOption): boolean => option.value === attendanceType)[0]
				?.label || null
		);
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

	_applicationFile: (param: RenderParams, metadataKey: "application_cv" | "application_cover_letter"): ReactNode => {
		const file = param.item?.[metadataKey];
		if (!file) return null;
		return (
			<div className="d-flex align-items-center gap-3 p-2 rounded border">
				<i className="bi bi-file-earmark fs-3 text-secondary flex-shrink-0" />
				<div className="flex-grow-1" style={{ minWidth: 0 }}>
					<div className="fw-medium text-truncate small">{file.filename}</div>
					<div className="text-muted" style={{ fontSize: "0.75rem" }}>
						{formatFileSize(file.size)}
					</div>
				</div>
				<div className="d-flex gap-1 flex-shrink-0">
					{canPreviewFile(file.type) && (
						<Button
							variant={"outline-secondary"}
							onClick={(): Promise<void> => filesApi.preview(file.id, param.token || "")}
							title="Preview"
							id={"preview-file-btn"}
						>
							<i className="bi bi-eye" />
						</Button>
					)}
					<Button
						variant={"outline-primary"}
						onClick={(): Promise<void> => filesApi.download(file.id, file.filename, param.token || "")}
						title="Download"
						id={"download-file-btn"}
					>
						<i className="bi bi-download" />
					</Button>
				</div>
			</div>
		);
	},

	applicationCv: (param: RenderParams): ReactNode => {
		return renderFunctions._applicationFile(param, "application_cv");
	},

	applicationCoverLetter: (param: RenderParams): ReactNode => {
		return renderFunctions._applicationFile(param, "application_cover_letter");
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
		if (!param.item?.date) return null;
		return toDdMmYyyyHhMm(param.item?.date);
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
		return getTrueFalseBadge(param.item?.premium?.is_active);
	},

	jobRatingActive: (param: RenderParams): ReactNode => {
		return getTrueFalseBadge(param.item?.premium?.job_rating_active);
	},

	jobScrapingActive: (param: RenderParams): ReactNode => {
		return getTrueFalseBadge(param.item?.premium?.job_scraping_active);
	},

	isActive: (param: RenderParams): ReactNode => {
		return getTrueFalseBadge(param.item?.is_active);
	},

	isImported: (param: RenderParams): ReactNode => {
		return getTrueFalseBadge(param.item?.is_imported);
	},

	isRecruiter: (param: RenderParams): ReactNode => {
		return getTrueFalseBadge(param.item?.is_recruiter);
	},

	isFavourite: (param: RenderParams): ReactNode => {
		const isFav: boolean = Boolean(param.item?.is_favourite);
		return (
			<i
				className={`bi ${isFav ? "bi-star-fill" : "bi-star"}`}
				style={{
					fontSize: param.view ? "1.4rem" : "1rem",
					color: isFav ? "#f5c518" : "var(--bs-secondary-color)",
				}}
			/>
		);
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
								style={{ fontSize: param.view ? "1.4rem" : "1rem", cursor: "auto" }}
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
				(option: SelectOption): boolean => option.value === param.item?.application_status
			)[0]?.label || null;
		if (status) {
			return <span className={`badge ${getApplicationStatusBadgeClass(status)} badge`}>{status}</span>;
		}
	},

	sourceType: (param: RenderParams): ReactNode => {
		const sourceType: string | null =
			sourceTypeOptions.filter((option: SelectOption): boolean => option.value === param.item?.source_type)[0]
				?.label || null;
		if (sourceType) {
			return <span className={`bg-primary badge`}>{sourceType}</span>;
		}
	},

	locationMap: (param: RenderParams): ReactNode => {
		return <LocationMap geolocatedEntry={[param.item]} />;
	},

	locationAttendance: (param: RenderParams): ReactNode => {
		const attendanceLabel: string | null =
			attendanceTypeOptions.find((o: SelectOption): boolean => o.value === param.item.attendance_type)?.label ??
			null;
		if (!attendanceLabel) return param.item.location ?? null;
		return (
			<>
				{param.item.location}
				<br />({attendanceLabel})
			</>
		);
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

	jobRatingSection: (param: RenderParams): ReactNode => {
		return <JobRatingSection scrapedJob={param.item} />;
	},

	platform: (param: RenderParams): ReactNode => {
		const names: Record<string, string> = {
			linkedin: "LinkedIn",
			nhs: "NHS Jobs",
			indeed: "Indeed",
			veganjobs: "VeganJobs",
		};
		return names[param.item?.platform] || param.item?.platform;
	},

	scrapingStatus: (param: RenderParams): ReactNode => {
		if (!param.item) return null;
		if (param.item.is_failed) return <span className="badge bg-danger">Failed</span>;
		if (!param.item.is_processed && param.item.scrape_error?.length) {
			return <span className="badge bg-warning text-dark">Retrying ({param.item.retry_count}/3)</span>;
		}
		if (!param.item.is_processed) return <span className="badge bg-secondary">Pending</span>;
		return <span className="badge bg-success">Scraped</span>;
	},

	// ----------------------------------------------------- COUNTS ----------------------------------------------------

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

	interviewCount: (param: RenderParams): number => {
		return param.item?.interviews?.length || 0;
	},

	jobApplicationUpdateCount: (param: RenderParams): number => {
		return param.item?.updates?.length || 0;
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

	locationBadge: (param: RenderParams): ReactNode => {
		const locationString: string | null = param.item.location;
		if (!locationString && !param.item?.attendance_type) return null;
		const attendanceLabel: string | null =
			attendanceTypeOptions.find((o: SelectOption): boolean => o.value === param.item.attendance_type)?.label ??
			null;
		let displayText: string = locationString || attendanceLabel || "";
		if (locationString && attendanceLabel) displayText = `${locationString} (${attendanceLabel})`;
		return (
			<LocationBadge
				item={param.item}
				badgeId={param.id}
				displayText={displayText}
				icon={getLocationIcon(param.item.attendance_type)}
			/>
		);
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
		return renderFunctions._aggregatorBadge(param, "source_aggregator_id");
	},

	KeywordBadges: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const keywords: KeywordData[] = getJamDataList(ctx.keywords, param.item?.keywords);

		if (keywords.length > 0) {
			return (
				<div className="badge-group" style={param.view ? { rowGap: "0.35rem" } : { rowGap: "0.15rem" }}>
					{keywords.map(
						(keyword: KeywordData, index: number): JSX.Element => (
							<span key={keyword.id || index} className="me-1">
								<KeywordBadge item={keyword} badgeId={`${param.id}-${index}`} />
							</span>
						)
					)}
				</div>
			);
		}
		return null;
	},

	_personBadges: (param: RenderParams, key: string, parent: JamData, menuItemKeys?: string[]): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const persons: PersonData[] = getJamDataList(ctx.persons, param.item?.[key]);

		if (persons.length > 0) {
			return (
				<div className="badge-group" style={param.view ? { rowGap: "0.35rem" } : { rowGap: "0.15rem" }}>
					{persons.map(
						(person: PersonData, index: number): JSX.Element => (
							<span key={person.id || index} className="me-1">
								<PersonBadge
									item={person}
									badgeId={`${param.id}-${index}`}
									menuItemKeys={menuItemKeys}
									parentItem={parent}
								/>
							</span>
						)
					)}
				</div>
			);
		}
		return null;
	},

	_personBadge: (param: RenderParams, idKey: keyof JobData): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const person: PersonData | undefined = getJamData(ctx.persons, param.item?.[idKey]);

		if (person) {
			return <PersonBadge item={person} badgeId={param.id} />;
		}
		return null;
	},

	ContactBadges: (param: RenderParams, menuItemKeys?: string[]): ReactNode => {
		return renderFunctions._personBadges(param, "contacts", param.item, menuItemKeys);
	},

	InterviewerBadges: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const job: EnrichedJobData = getJamData(ctx.jobs, param.item?.job_id)!;
		return renderFunctions._personBadges(param, "interviewers", job);
	},

	recruiterBadge: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const person: PersonData | undefined = getJamData(ctx.persons, param.item?.recruiter_id);

		if (person) {
			return <PersonBadge item={person} badgeId={param.id} />;
		}
		return null;
	},

	recruitmentCompanyBadge: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const company: CompanyData | undefined = getJamData(ctx.companies, param.item?.recruitment_company_id);

		if (company) {
			return <CompanyBadge item={company} badgeId={param.id} />;
		}
		return null;
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

	_accordionJobTable: (param: RenderParams, key: string, label?: string): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const jobs: EnrichedJobData[] = filterByKey(ctx.jobs, key, param.item?.id);
		if (jobs.length > 0) {
			return (
				<AccordionTable
					title={label || "Jobs"}
					data={jobs}
					icon={getTableIcon("Jobs")}
					helpText={param.helpText}
				>
					{(data: EnrichedJobData[]) => <JobsTable data={data} columns={param.columns} />}
				</AccordionTable>
			);
		} else {
			return "";
		}
	},

	AccordionInterviewTable: (param: RenderParams, key: string, label?: string): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const interviews: InterviewData[] = filterByKey(ctx.interviews, key, param.item?.id);
		if (interviews.length > 0) {
			return (
				<AccordionTable
					title={label || "Interviews"}
					data={interviews}
					icon={getTableIcon("Interviews")}
					helpText={param.helpText}
				>
					{(data: InterviewData[]) => <InterviewsTable data={data} showAdd={false} columns={param.columns} />}
				</AccordionTable>
			);
		} else {
			return "";
		}
	},

	accordionJobApplicationTable: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const jobs: EnrichedJobData[] = filterByKey(ctx.jobs, "application_aggregator_id", param.item?.id);
		if (jobs.length > 0) {
			return (
				<AccordionTable
					title={param.label || "Job Applications"}
					data={jobs}
					icon={getTableIcon("Job Applications")}
					helpText={param.helpText}
				>
					{(data: EnrichedJobData[]) => <JobsTable data={data} columns={param.columns} />}
				</AccordionTable>
			);
		} else {
			return "";
		}
	},

	AccordionPersonTable: (param: RenderParams): ReactNode => {
		const ctx: DataContextValue = param.dataContext;
		const persons: PersonData[] = filterByKey(ctx.persons, "company_id", param.item?.id);
		if (persons.length > 0) {
			return (
				<AccordionTable
					title={param.label || "Persons"}
					data={persons}
					icon={getTableIcon("People")}
					helpText={param.helpText}
				>
					{(data: PersonData[]) => <PersonTable data={data} columns={param.columns} />}
				</AccordionTable>
			);
		} else {
			return "";
		}
	},

	accordionScrapedJobTable: (param: RenderParams) => <AccordionScrapedJobTable param={param} />,

	emailScrapedJobTable: (param: RenderParams) => <EmailScrapedJobTable param={param} />,

	emailScrapedJobTableReadOnly: (param: RenderParams) => <EmailScrapedJobTable param={param} viewOnly={true} />,

	scrapedJobEmailTable: (param: RenderParams) => <ScrapedJobEmailTable param={param} />,
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

	if (rendered !== null && rendered !== undefined) {
		return <>{rendered}</>;
	} else {
		return <span className="text-muted">Not Provided</span>;
	}
};

export const IsViewNull = (
	dataContext: DataContextValue,
	token: string,
	field: ViewField,
	item: any,
	id: string
): boolean => {
	let rendered: ReactNode;
	if (field.render) {
		const renderParams: RenderParams = {
			item: item,
			view: false,
			id: `${id}-${field.key}`,
			columns: field.columns,
			helpText: field.helpText,
			dataContext: dataContext,
			token: token,
		};
		rendered = field.render(renderParams);
	} else {
		rendered = item?.[field.key];
	}

	return rendered == null;
};

interface GenericAccordionProps<T = any> {
	title: string;
	data: T[];
	children: (data: T[], onChange?: () => void) => React.ReactNode;
	icon?: string;
	defaultOpen?: boolean;
	helpText?: string;
}

export const AccordionTable = <T,>({
	title,
	data,
	children,
	icon,
	defaultOpen = false,
	helpText,
}: GenericAccordionProps<T>): JSX.Element => {
	return (
		<Accordion
			defaultOpen={defaultOpen}
			header={
				<>
					{icon && <i className={`bi-${icon} me-2`}></i>}
					<span className="fw-medium">{title}</span>
					<span className="text-muted ms-2">({data?.length || 0})</span>
					{helpText && <HelpBubble helpText={helpText} size="15px" />}
				</>
			}
		>
			<div className={"mt-2"}>{children(data)}</div>
		</Accordion>
	);
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
		<AccordionTable
			title="Filtered Jobs"
			data={data}
			icon={getTableIcon("Scraped Jobs")}
			helpText="Scraped Jobs that were filtered by this filter."
		>
			{(rows: ScrapedJobData[]) => <ScrapedJobsTableReadOnly data={rows} columns={param.columns} />}
		</AccordionTable>
	);
};

const EmailScrapedJobTable: React.FC<{ param: RenderParams; viewOnly?: boolean }> = ({ param, viewOnly = false }) => {
	const [data, setData] = useState<ScrapedJobData[] | null>(null);
	const [loading, setLoading] = useState<boolean>(true);
	const [reloadTick, setReloadTick] = useState<number>(0);

	useEffect(() => {
		const fetchData = async (): Promise<void> => {
			if (!param.token || !param.item.id) return;
			if (data === null) setLoading(true);
			try {
				const response = await scrapedJobApi.getByEmailId(param.item.id, param.token);
				setData(response.data);
			} catch (error) {
				console.error("Error fetching scraped jobs for email:", error);
				setData([]);
			} finally {
				setLoading(false);
			}
		};

		fetchData().then();
	}, [param.item.id, param.token, reloadTick]);

	if (loading) return <LoadingSpinner size={"sm"} />;
	if (!data?.length) return null;

	return (
		<ScrapedJobsTableReadOnly
			data={data}
			columns={param.columns}
			onSuccess={() => setReloadTick((t) => t + 1)}
			viewOnly={viewOnly}
		/>
	);
};

const ScrapedJobEmailTable: React.FC<{ param: RenderParams }> = ({ param }) => {
	const [data, setData] = useState<JobEmailData[] | null>(null);
	const [loading, setLoading] = useState<boolean>(true);

	useEffect(() => {
		const fetchData = async (): Promise<void> => {
			if (!param.token || !param.item.id) return;
			setLoading(true);
			try {
				const response = await jobEmailApi.getByScrapedJobId(param.item.id, param.token);
				setData(response.data);
			} catch (error) {
				console.error("Error fetching emails for scraped job:", error);
				setData([]);
			} finally {
				setLoading(false);
			}
		};

		fetchData().then();
	}, [param.item.id, param.token]);

	if (loading) return <LoadingSpinner size={"sm"} />;
	if (!data?.length) return null;
	return <JobEmailTableReadOnly data={data} modalProps={{ scrapedJobsReadOnly: true }} />;
};
