import React, { ReactElement, ReactNode, useState } from "react";
import { LocationModal } from "../../modals/LocationModal";
import { CompanyModal } from "../../modals/CompanyModal";
import { PersonModal } from "../../modals/PersonModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { AggregatorModal } from "../../modals/AggregatorModal";
import { accessAttribute } from "../../../utils/Utils";
import InterviewsTable from "../../tables/InterviewTable";
import JobApplicationUpdateTable from "../../tables/JobApplicationUpdateTable";
import { JobAndApplicationModal } from "../../modals/JobAndApplicationModal";
import { THEMES } from "../../../utils/Theme";
import LocationMap from "../../maps/LocationMap";
import {
	AggregatorOut,
	CompanyOut,
	JobData,
	KeywordOut,
	LocationCreate,
	LocationOut,
	PersonOut,
} from "../../../services/Schemas";
import JobsTable from "../../tables/JobTable";
import PersonTable from "../../tables/PersonTable";
import { TableColumn } from "./TableColumnRenders";

interface ModalManagerProps {
	children: (handleClick: (item: any) => void) => ReactNode;
}

export interface RenderParams {
	item: any;
	view?: boolean;
	accessKey?: string | undefined;
	id?: string;
	columns?: TableColumn[];
}

export interface Field {
	key: string;
	render?: (params: RenderParams) => ReactNode;
	accessKey?: string;
	columns?: TableColumn[];
}

interface ModalManagerProps {
	children: (handleClick: (item: any) => void) => ReactNode;
}

type FlexibleModalComponent = React.ComponentType<any>;

const createModalManager = (ModalComponent: FlexibleModalComponent) => {
	return ({ children }: ModalManagerProps): ReactElement => {
		const [showModal, setShowModal] = useState<boolean>(false);
		const [selectedItem, setSelectedItem] = useState<any>(null);
		const [selectedId, setSelectedId] = useState<string | number | null>(null);

		const handleClick = (itemId: number): void => {
			setSelectedItem(null);
			setSelectedId(itemId);
			setShowModal(true);
		};

		const handleHide = () => {
			setShowModal(false);
			setTimeout(() => {
				setSelectedItem(null);
				setSelectedId(null);
			}, 300);
		};

		// Empty handlers for modal callbacks since we're just viewing
		const handleSuccess = () => {};
		const handleDelete = () => {};

		return (
			<>
				{children(handleClick)}
				<ModalComponent
					show={showModal}
					onHide={handleHide}
					data={selectedItem}
					id={selectedId}
					submode="view"
					onSuccess={handleSuccess}
					onDelete={handleDelete}
					onJobSuccess={handleSuccess}
					onApplicationSuccess={handleSuccess}
					onJobDelete={handleDelete}
					onApplicationDelete={handleDelete}
				/>
			</>
		);
	};
};

const LocationModalManager = createModalManager(LocationModal);
const CompanyModalManager = createModalManager(CompanyModal);
const PersonModalManager = createModalManager(PersonModal);
const KeywordModalManager = createModalManager(KeywordModal);
const JobAndApplicationModalManager = createModalManager(JobAndApplicationModal);
const AggregatorModalManager = createModalManager(AggregatorModal);

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

const accessSubAttribute = (item: any, accessKey: string | undefined, key: string): any => {
	if (accessKey) {
		item = accessAttribute(item, accessKey);
	}
	return item?.[key];
};

interface GenericAccordionProps<T = any> {
	title: string;
	data: T[];
	onChange?: () => void;
	itemId?: number;
	children: (data: T[], onChange?: () => void) => React.ReactNode;
	icon?: string;
	defaultOpen?: boolean;
}

export const GenericAccordion = <T,>({
	title,
	data,
	onChange,
	children,
	icon,
	defaultOpen = false,
}: GenericAccordionProps<T>) => {
	const [isOpen, setIsOpen] = React.useState(defaultOpen);

	return (
		<div className="simple-accordion" style={{ paddingLeft: "10px", paddingRight: "10px" }}>
			<div
				className="simple-accordion-header d-flex align-items-center justify-content-between py-2 border-bottom"
				onClick={() => setIsOpen(!isOpen)}
				style={{ cursor: "pointer" }}
			>
				<div className="d-flex align-items-center">
					{icon && <i className={`${icon} me-2`}></i>}
					<span className="fw-medium">{title}</span>
					<span className="text-muted ms-2">({data?.length || 0})</span>
				</div>
				<i className={`bi ${isOpen ? "bi-chevron-up" : "bi-chevron-down"} text-muted`}></i>
			</div>
			{isOpen && <div className="simple-accordion-content">{children(data, onChange)}</div>}
		</div>
	);
};

export const renderFunctions = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	_longText: (param: RenderParams, key: string): ReactNode => {
		const text = accessSubAttribute(param.item, param.accessKey, key);
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

	appTheme: (param: RenderParams): ReactNode => {
		const themeKey = accessSubAttribute(param.item, param.accessKey, "theme");
		if (themeKey) {
			const theme = THEMES.find((theme) => theme.key === themeKey);
			return theme?.name;
		}
		return null;
	},

	updateType: (param: RenderParams): ReactNode => {
		const updateType = accessSubAttribute(param.item, param.accessKey, "type");
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
		const url = accessSubAttribute(param.item, param.accessKey, attribute);
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
		const email = accessSubAttribute(param.item, param.accessKey, "email");
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
		const linkedinUrl = accessSubAttribute(param.item, param.accessKey, "linkedin_url");
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
		const date = accessSubAttribute(param.item, param.accessKey, key);
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

	date: (param: RenderParams): string | null => {
		return renderFunctions._date(param, "date");
	},

	datetime: (param: RenderParams): string | null => {
		const date = accessSubAttribute(param.item, param.accessKey, "date");
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
		const phone = accessSubAttribute(param.item, param.accessKey, "phone");
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
		const isAdmin = accessSubAttribute(param.item, param.accessKey, "is_admin");
		const icon = getAdminIcon(isAdmin);
		return <i className={icon}></i>;
	},

	salaryRange: (param: RenderParams): string | null => {
		const salary_min = accessSubAttribute(param.item, param.accessKey, "salary_min");
		const salary_max = accessSubAttribute(param.item, param.accessKey, "salary_max");
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
		const personal_rating = accessSubAttribute(param.item, param.accessKey, "personal_rating");
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

	status: (param: RenderParams): ReactNode => {
		const status = accessSubAttribute(param.item, param.accessKey, "application_status");
		if (status) {
			return <span className={`badge ${getApplicationStatusBadgeClass(status)} badge`}>{status}</span>;
		}
	},

	locationMap: (param: RenderParams): ReactNode => {
		const locations: LocationCreate[] = param.item ? [param.item] : [];
		return <LocationMap locations={locations} />;
	},

	lastUpdateDays: (params: RenderParams): ReactNode => {
		const daysSinceLastUpdate = accessSubAttribute(params.item, params.accessKey, "days_since_last_update");
		return <span className={"text-danger"}>{daysSinceLastUpdate} days</span>;
	},

	// ----------------------------------------------------- COUNTS ----------------------------------------------------

	interviewCount: (param: RenderParams): number => {
		const interviews = accessSubAttribute(param.item, param.accessKey, "interviews");
		return interviews?.length || 0;
	},

	updateCount: (param: RenderParams): number => {
		const updates = accessSubAttribute(param.item, param.accessKey, "updates");
		return updates?.length || 0;
	},

	jobCount: (param: RenderParams): number => {
		const jobs = accessSubAttribute(param.item, param.accessKey, "jobs");
		return jobs?.length || 0;
	},

	jobApplicationCount: (param: RenderParams): number => {
		const jobs = accessSubAttribute(param.item, param.accessKey, "job_applications");
		return jobs?.length || 0;
	},

	personCount: (param: RenderParams): number => {
		const persons = accessSubAttribute(param.item, param.accessKey, "persons");
		return persons?.length || 0;
	},

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	_jobBadge: (param: RenderParams, attribute: string, displayAttribute: keyof JobData): ReactNode => {
		const job: JobData = accessSubAttribute(param.item, param.accessKey, attribute);
		if (job) {
			return (
				<JobAndApplicationModalManager>
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
				</JobAndApplicationModalManager>
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
		const keywords: KeywordOut[] = accessSubAttribute(param.item, param.accessKey, "keywords");
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
		const location: LocationOut = accessSubAttribute(param.item, param.accessKey, "location");
		const attendanceType = accessAttribute(param.item, "attendance_type");

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
			if (attendanceType === "on-site") {
				displayText = `${location.name} (On-site)`;
			} else if (attendanceType === "hybrid") {
				displayText = `${location.name} (Hybrid)`;
			}

			return (
				<LocationModalManager>
					{(handleClick) => (
						<span
							className={`badge bg-warning clickable-badge`}
							onClick={() => handleClick(location.id)}
							id={param.id}
						>
							<i className="bi bi-geo-alt me-1"></i>
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
		const company: CompanyOut = accessSubAttribute(param.item, param.accessKey, "company");
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
		const persons: PersonOut[] = accessSubAttribute(param.item, param.accessKey, key);
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
		const appliedVia = accessSubAttribute(param.item, param.accessKey, "applied_via");
		if (appliedVia === "aggregator") {
			return renderFunctions.applicationAggregatorBadge(param);
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
		const aggregator: AggregatorOut = accessSubAttribute(param.item, param.accessKey, attribute);
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

	aggregator: (param: RenderParams): ReactNode => {
		// TODO missing source for the jobs
		return renderFunctions._aggregatorBadge(param, "aggregator");
	},

	applicationAggregatorBadge: (param: RenderParams): ReactNode => {
		return renderFunctions._aggregatorBadge(param, "application_aggregator");
	},

	// ----------------------------------------------------- TABLES ----------------------------------------------------

	interviewTable: (param: RenderParams): ReactNode => {
		const interviews = accessSubAttribute(param.item, param.accessKey, "interviews");
		const onChange = () => {}; // Empty function to satisfy the required prop
		return <InterviewsTable data={interviews} jobApplicationId={param.item.id} onChange={onChange} />;
	},

	jobApplicationUpdateTable: (param: RenderParams): ReactNode => {
		const updates = accessSubAttribute(param.item, param.accessKey, "updates");
		const onChange = () => {}; // Empty function to satisfy the required prop
		return <JobApplicationUpdateTable data={updates} jobApplicationId={param.item.id} onChange={onChange} />;
	},

	// ------------------------------------------------ ACCORDION TABLES -----------------------------------------------

	accordionJobTable: (param: RenderParams): ReactNode => {
		const jobs = accessSubAttribute(param.item, param.accessKey, "jobs");
		const onChange = () => {};
		return (
			<GenericAccordion title="Jobs" data={jobs} onChange={onChange} icon={getTableIcon("Jobs")}>
				{(data, onChangeCallback) => (
					<JobsTable onChange={onChangeCallback} data={data} columns={param.columns} />
				)}
			</GenericAccordion>
		);
	},

	accordionInterviewTable: (param: RenderParams): ReactNode => {
		const interviews = accessSubAttribute(param.item, param.accessKey, "interviews");
		const onChange = () => {};
		return (
			<GenericAccordion
				title="Interviews"
				data={interviews}
				onChange={onChange}
				icon={getTableIcon("Interviews")}
			>
				{(data, onChangeCallback) => (
					<InterviewsTable data={data} onChange={onChangeCallback} showAdd={false} columns={param.columns} />
				)}
			</GenericAccordion>
		);
	},

	accordionJobApplicationTable: (param: RenderParams): ReactNode => {
		const jobs = accessSubAttribute(param.item, param.accessKey, "job_applications");
		const onChange = () => {};
		return (
			<GenericAccordion
				title="Job Applications"
				data={jobs}
				onChange={onChange}
				icon={getTableIcon("Job Applications")}
			>
				{(data, onChangeCallback) => (
					<JobsTable data={data} onChange={onChangeCallback} columns={param.columns} />
				)}
			</GenericAccordion>
		);
	},

	accordionPersonTable: (param: RenderParams): ReactNode => {
		const persons = accessSubAttribute(param.item, param.accessKey, "persons");
		const onChange = () => {};
		return (
			<GenericAccordion title="Persons" data={persons} onChange={onChange} icon={getTableIcon("Persons")}>
				{(data, onChangeCallback) => (
					<PersonTable data={data} onChange={onChangeCallback} columns={param.columns} />
				)}
			</GenericAccordion>
		);
	},
};

export const renderViewElement = (field: Field, item: any, id: string): ReactNode => {
	const noText = <span className="text-muted">Not Provided</span>;

	let rendered: ReactNode;
	if (field.render) {
		const renderParams: RenderParams = {
			item: item,
			view: false,
			accessKey: field.accessKey,
			id: `${id}-${field.key}`,
			columns: field.columns,
		};
		rendered = field.render(renderParams);
	} else {
		if (field.accessKey) {
			item = item[field.accessKey];
		}
		rendered = item?.[field.key];
	}

	if (rendered !== null && rendered !== undefined) {
		// allow for 0
		return rendered;
	} else {
		return noText;
	}
};
