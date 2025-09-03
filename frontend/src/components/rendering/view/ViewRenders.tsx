import React, { ReactElement, ReactNode, useState } from "react";
import { LocationModal } from "../../modals/LocationModal";
import { CompanyModal } from "../../modals/CompanyModal";
import { PersonModal } from "../../modals/PersonModal";
import { KeywordModal } from "../../modals/KeywordModal";
import { JobApplicationModal } from "../../modals/JobApplicationModal";
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
	KeywordOut,
	LocationCreate,
	LocationOut,
	PersonOut,
} from "../../../services/Schemas";
import JobsTable from "../../tables/JobTable";

interface ModalComponentProps {
	show: boolean;
	onHide: () => void;
	data: any;
	id: string | number | null;
	submode?: string;
	size?: string;
	endpoint?: string;
	jobId?: string | number | null;
	onSuccess: (item: any) => void;
	onDelete: (item: any) => void;
	onJobSuccess?: (item: any) => void;
	onApplicationSuccess?: (item: any) => void;
	onJobDelete?: (item: any) => void;
	onApplicationDelete?: (item: any) => void;
}

interface ModalManagerProps {
	children: (handleClick: (item: any) => void) => ReactNode;
}

export interface RenderParams {
	item: any;
	view?: boolean;
	accessKey?: string | undefined;
	id?: string;
}

interface Job {
	id: string | number;
	title?: string;
	name?: string;
}

interface JobApplication {
	id: string | number;
	status: string;
}

interface Field {
	key: string;
	render?: (params: RenderParams) => ReactNode;
	accessKey?: string;
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
const JobApplicationModalManager = createModalManager(JobApplicationModal);
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
			return "bg-secondary";
		case "withdrawn":
			return "bg-light";
		default:
			return "bg-primary";
	}
};

const getUpdateTypeIcon = (type: string): string => {
	switch (type?.toLowerCase()) {
		case "received":
			return "bi-download";
		default:
			return "bi-upload";
	}
};

export const getTableIcon = (title: string): string => {
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
		<div className="accordion">
			<div className="accordion-item">
				<h2 className="accordion-header">
					<button
						className={`accordion-button ${isOpen ? "" : "collapsed"}`}
						type="button"
						onClick={() => setIsOpen(!isOpen)}
						aria-expanded={isOpen}
					>
						{icon && <i className={`${icon} me-2`}></i>}
						{title} ({data?.length || 0})
					</button>
				</h2>
				<div className={`accordion-collapse collapse ${isOpen ? "show" : ""}`}>
					<div className="accordion-body">{children(data, onChange)}</div>
				</div>
			</div>
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

	description: (param: RenderParams): ReactNode => {
		return renderFunctions._longText(param, "description");
	},

	url: (param: RenderParams): ReactNode => {
		const url = accessSubAttribute(param.item, param.accessKey, "url");
		if (url) {
			const safeUrl = ensureHttpPrefix(url);
			return (
				<a href={safeUrl} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					{safeUrl?.slice(8)} <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
		return null;
	},

	appTheme: (param: RenderParams): ReactNode => {
		const themeKey = accessSubAttribute(param.item, param.accessKey, "theme");
		if (themeKey) {
			const theme = THEMES.find((theme) => theme.key === themeKey);
			return theme?.name;
		}
		return null;
	},

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

	date: (param: RenderParams): string | null => {
		// TODO needed?
		return renderFunctions._date(param, "date");
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

	isAdmin: (param: RenderParams): ReactNode => {
		const isAdmin = accessSubAttribute(param.item, param.accessKey, "is_admin");
		return isAdmin ? (
			<i className="bi bi-check-circle-fill text-success"></i>
		) : (
			<i className="bi bi-x-circle-fill text-danger"></i>
		);
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
		const status = accessSubAttribute(param.item, param.accessKey, "status");
		return <span className={`badge ${getApplicationStatusBadgeClass(status)} badge`}>{status}</span>;
	},

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
		const job_applications = accessSubAttribute(param.item, param.accessKey, "job_applications");
		return job_applications?.length || 0;
	},

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	jobApplication: (param: RenderParams): ReactNode => {
		const job_application: JobApplication = accessSubAttribute(param.item, param.accessKey, "job_application");
		if (job_application) {
			return (
				<JobApplicationModalManager>
					{(handleClick) => (
						<span
							className={`badge ${getApplicationStatusBadgeClass(job_application.status)} clickable-badge`}
							onClick={() => handleClick(job_application.id)}
							id={param.id}
						>
							{job_application.status}
						</span>
					)}
				</JobApplicationModalManager>
			);
		}
		return null;
	},

	job: (param: RenderParams): ReactNode => {
		const job: Job = accessSubAttribute(param.item, param.accessKey, "job");
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
							{job.title}
						</span>
					)}
				</JobAndApplicationModalManager>
			);
		}
		return null;
	},

	jobName: (param: RenderParams): ReactNode => {
		const job: Job = accessSubAttribute(param.item, param.accessKey, "job");
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
							{job.name}
						</span>
					)}
				</JobAndApplicationModalManager>
			);
		}
		return null;
	},

	keywords: (param: RenderParams): ReactNode => {
		const keywords: KeywordOut[] = accessSubAttribute(param.item, param.accessKey, "keywords");
		if (keywords?.length > 0) {
			return (
				<div>
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

	location: (param: RenderParams): ReactNode => {
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

	company: (param: RenderParams): ReactNode => {
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

	_persons: (param: RenderParams, key: string): ReactNode => {
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

	contacts: (param: RenderParams): ReactNode => {
		return renderFunctions._persons(param, "contacts");
	},

	interviewers: (param: RenderParams): ReactNode => {
		return renderFunctions._persons(param, "interviewers");
	},

	appliedVia: (param: RenderParams): ReactNode => {
		const appliedVia = accessSubAttribute(param.item, param.accessKey, "applied_via");
		if (appliedVia === "aggregator") {
			return renderFunctions.aggregator(param);
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

	aggregator: (param: RenderParams): ReactNode => {
		const aggregator: AggregatorOut = accessSubAttribute(param.item, param.accessKey, "aggregator");
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

	jobTable: (param: RenderParams): ReactNode => {
		const jobs = accessSubAttribute(param.item, param.accessKey, "jobs");
		const onChange = () => {};
		return (
			<GenericAccordion title="Jobs" data={jobs} onChange={onChange} icon={getTableIcon("Jobs")}>
				{(data, onChangeCallback) => <JobsTable data={data} onChange={onChangeCallback} />}
			</GenericAccordion>
		);
	},

	locationMap: (param: RenderParams): ReactNode => {
		const locations: LocationCreate[] = param.item ? [param.item] : [];
		return <LocationMap locations={locations} />;
	},
};

export const renderFieldValue = (field: Field, item: any, id: string): ReactNode => {
	const noText = <span className="text-muted">Not Provided</span>;

	let rendered: ReactNode;
	if (field.render) {
		rendered = field.render({
			item,
			view: false,
			accessKey: field.accessKey,
			id: `${id}-${field.key}`,
		});
	} else {
		rendered = item?.[field.key];
	}

	if (rendered !== null && rendered !== undefined) {
		// allow for 0
		return rendered;
	} else {
		return noText;
	}
};
