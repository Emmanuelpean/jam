import React, { useState } from "react";
import { LocationViewModal } from "../../modals/LocationModal";
import { CompanyViewModal } from "../../modals/CompanyModal";
import { PersonViewModal } from "../../modals/PersonModal";
import { KeywordViewModal } from "../../modals/KeywordModal";
import { JobApplicationViewModal } from "../../modals/JobApplicationModal";
import { AggregatorViewModal } from "../../modals/AggregatorModal";
import { JobViewModal } from "../../modals/_JobModal";
import { accessAttribute } from "../../../utils/Utils.ts";
import { filesApi } from "../../../services/Api.ts";
import { useAuth } from "../../../contexts/AuthContext.tsx";
import InterviewsTable from "../../tables/InterviewTable";
import JobApplicationUpdateTable from "../../tables/JobApplicationUpdateTable";
import { THEMES } from "../../../utils/Theme.ts";
import { type } from "@testing-library/user-event/dist/type";
import { useGlobalToast } from "../../../hooks/useNotificationToast.ts";
import LocationMap from "../../maps/LocationMap";

const createModalManager = (ModalComponent) => {
	return ({ children }) => {
		const [showModal, setShowModal] = useState(false);
		const [selectedItem, setSelectedItem] = useState(null);

		const handleClick = (item) => {
			setSelectedItem(item);
			setShowModal(true);
		};

		return (
			<>
				{children(handleClick)}
				{showModal && selectedItem && (
					<ModalComponent
						show={showModal}
						onHide={() => {
							setShowModal(false);
							setSelectedItem(null);
						}}
						data={selectedItem}
					/>
				)}
			</>
		);
	};
};

const LocationModalManager = createModalManager(LocationViewModal);
const CompanyModalManager = createModalManager(CompanyViewModal);
const PersonModalManager = createModalManager(PersonViewModal);
const KeywordModalManager = createModalManager(KeywordViewModal);
const JobApplicationModalManager = createModalManager(JobApplicationViewModal);
const JobModalManager = createModalManager(JobViewModal);
const AggregatorModalManager = createModalManager(AggregatorViewModal);

export const getApplicationStatusBadgeClass = (status) => {
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

const getUpdateTypeIcon = (type) => {
	switch (type?.toLowerCase()) {
		case "received":
			return "bi-download";
		case "sent":
			return "bi-upload";
	}
};

const ensureHttpPrefix = (url) => {
	if (!url) return url;
	if (url.match(/^https?:\/\//)) return url;
	return `https://${url}`;
};

const FileBadge = ({ file, icon, label }) => {
	const { token } = useAuth();
	const { showSuccess, showError } = useGlobalToast();

	const handleDownload = async (e) => {
		e.stopPropagation();
		e.preventDefault();

		if (file && file.id && file.filename) {
			try {
				await filesApi.download(file.id, file.filename, token);
				showSuccess(`File ${file.filename} downloaded successfully.`);
			} catch (error) {
				showError("Error downloading file. Please try again later.");
			}
		}
	};

	if (!file || !file.id) return null;

	return (
		<span
			className={`badge clickable-badge me-1`}
			onClick={handleDownload}
			style={{ cursor: "pointer", backgroundColor: "green" }}
			title={`Download ${file.filename}`}
		>
			<i className={`${icon} me-1`}></i>
			{label}
			<i className="bi bi-download ms-1"></i>
		</span>
	);
};

const accessSubAttribute = (item, accessKey, key) => {
	if (accessKey) {
		item = accessAttribute(item, accessKey);
	}
	return item?.[key];
};

export const renderFunctions = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	_longText: (item, view = false, accessKey, key) => {
		const text = accessSubAttribute(item, accessKey, key);
		if (text) {
			if (view) {
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
	},

	note: (item, view = false, accessKey) => {
		return renderFunctions._longText(item, view, accessKey, "note");
	},

	description: (item, view = false, accessKey) => {
		return renderFunctions._longText(item, view, accessKey, "description");
	},

	url: (item, view = false, accessKey) => {
		const url = accessSubAttribute(item, accessKey, "url");
		if (url) {
			const safeUrl = ensureHttpPrefix(url);
			return (
				<a href={safeUrl} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					{safeUrl.slice(8)} <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
	},

	appTheme: (item, view = false, accessKey) => {
		const themeKey = accessSubAttribute(item, accessKey, "theme");
		if (themeKey) {
			return THEMES.find((theme) => theme.key === themeKey).name;
		}
	},

	_datetime: (date) => {
		if (date) {
			return new Date(date).toLocaleDateString();
		}
	},

	lastLogin: (item, view = false, accessKey) => {
		const date = accessSubAttribute(item, accessKey, "last_login");
		return renderFunctions._datetime(date);
	},

	createdDate: (item, view = false, accessKey) => {
		const date = accessSubAttribute(item, accessKey, "created_at");
		return renderFunctions._datetime(date);
	},

	datetime: (item, view = false, accessKey) => {
		const date = accessSubAttribute(item, accessKey, "date");
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
	},

	date: (item, view = false, key = "date") => {
		const date = accessAttribute(item, key);
		return renderFunctions._datetime(date);
	},

	email: (item, view = false, accessKey) => {
		const email = accessSubAttribute(item, accessKey, "email");
		if (email)
			return (
				<a href={`mailto:${email}`} className="text-decoration-none">
					<i className="bi bi-envelope me-1"></i>
					{email}
				</a>
			);
	},

	phone: (item, view = false, accessKey) => {
		const phone = accessSubAttribute(item, accessKey, "phone");
		if (phone) {
			return (
				<a href={`tel:${phone}`} className="text-decoration-none">
					<i className="bi bi-telephone me-1"></i>
					{phone}
				</a>
			);
		}
	},

	linkedinUrl: (item, view = false, accessKey) => {
		const url = accessSubAttribute(item, accessKey, "linkedin_url");
		if (url) {
			return (
				<a href={url} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					<i className="bi bi-linkedin me-1"></i>
					Profile <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
	},

	isAdmin: (item, view = false, accessKey) => {
		const isAdmin = accessSubAttribute(item, accessKey, "is_admin");
		return isAdmin ? (
			<i className="bi bi-check-circle-fill text-success"></i>
		) : (
			<i className="bi bi-x-circle-fill text-danger"></i>
		);
	},

	updateType: (item, view = false, accessKey) => {
		const type = accessSubAttribute(item, accessKey, "type");
		if (type) {
			const capitalizedType = type.charAt(0).toUpperCase() + type.slice(1);
			let icon = getUpdateTypeIcon(type);

			return (
				<span>
					{icon && <i className={`${icon} me-1`}></i>}
					{capitalizedType}
				</span>
			);
		}
	},

	salaryRange: (item, view = false, accessKey) => {
		const salary_min = accessSubAttribute(item, accessKey, "salary_min");
		const salary_max = accessSubAttribute(item, accessKey, "salary_max");
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
	},

	personalRating: (item, view = false, acccessKey) => {
		const personal_rating = accessSubAttribute(item, acccessKey, "personal_rating");
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

	status: (item, view = false, acccessKey) => {
		const status = accessSubAttribute(item, acccessKey, "status");
		return <span className={`badge ${getApplicationStatusBadgeClass(status)} badge`}>{status}</span>;
	},

	interviewCount: (item, view = false, acccessKey) => {
		const interviews = accessSubAttribute(item, acccessKey, "interviews");
		return interviews.length;
	},

	updateCount: (item, view = false, acccessKey) => {
		const updates = accessSubAttribute(item, acccessKey, "updates");
		return updates.length;
	},

	// --------------------------------------------------- FILE BADGES -------------------------------------------------

	files: (item, view = false, accessKey) => {
		const cv = accessSubAttribute(item, accessKey, "cv");
		const coverLetter = accessSubAttribute(item, accessKey, "cover_letter");
		if (!cv && !coverLetter) return null;

		return (
			<div>
				{cv && <FileBadge file={cv} icon="bi bi-file-text" label="CV" />}
				{coverLetter && <FileBadge file={coverLetter} icon="bi bi-file-text" label="Cover Letter" />}
			</div>
		);
	},

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	jobApplication: (item, view = false, accessKey, id) => {
		const job_application = accessSubAttribute(item, accessKey, "job_application");
		if (job_application) {
			return (
				<JobApplicationModalManager>
					{(handleClick) => (
						<span
							className={`badge ${getApplicationStatusBadgeClass(job_application.status)} clickable-badge`}
							onClick={() => handleClick(job_application)}
							id={id}
						>
							{job_application.status}
						</span>
					)}
				</JobApplicationModalManager>
			);
		}
	},

	job: (item, view = false, accessKey, id) => {
		const job = accessSubAttribute(item, accessKey, "job");
		if (job) {
			return (
				<JobModalManager>
					{(handleClick) => (
						<span className={`badge bg-info clickable-badge`} onClick={() => handleClick(job)} id={id}>
							<i className="bi bi-briefcase me-1"></i>
							{job.title}
						</span>
					)}
				</JobModalManager>
			);
		}
	},

	jobName: (item, view = false, accessKey, id) => {
		const job = accessSubAttribute(item, accessKey, "job");
		if (job) {
			return (
				<JobModalManager>
					{(handleClick) => (
						<span className={`badge bg-info clickable-badge`} onClick={() => handleClick(job)} id={id}>
							<i className="bi bi-briefcase me-1"></i>
							{job.name}
						</span>
					)}
				</JobModalManager>
			);
		}
	},

	keywords: (item, view = false, accessKey, id) => {
		const keywords = accessSubAttribute(item, accessKey, "keywords");
		if (keywords && keywords.length > 0) {
			return (
				<div>
					{keywords.map((keyword, index) => (
						<span key={keyword.id || index} className="me-1">
							<KeywordModalManager>
								{(handleClick) => (
									<span
										className="badge bg-info clickable-badge"
										onClick={() => handleClick(keyword)}
										id={id + "-" + index}
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
	},

	location: (item, view = false, accessKey, id) => {
		const location = accessSubAttribute(item, accessKey, "location");
		const attendanceType = accessAttribute(item, "attendance_type");
		if (attendanceType === "remote") {
			return (
				<span className="badge bg-warning" id={id}>
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
							onClick={() => handleClick(location)}
							id={id}
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
				<span className="badge bg-warning" id={id}>
					<i className="bi bi-building me-1"></i>
					{attendanceType.charAt(0).toUpperCase() + attendanceType.slice(1)}
				</span>
			);
		}

		return null;
	},

	company: (item, view = false, accessKey, id) => {
		const company = accessSubAttribute(item, accessKey, "company");
		if (company) {
			return (
				<CompanyModalManager>
					{(handleClick) => (
						<span className={"badge bg-info clickable-badge"} onClick={() => handleClick(company)} id={id}>
							<i className="bi bi-building me-1"></i>
							{company.name}
						</span>
					)}
				</CompanyModalManager>
			);
		}
	},

	_persons: (item, view = false, accessKey, id, key) => {
		const persons = accessSubAttribute(item, accessKey, key);
		if (persons && persons.length > 0) {
			return (
				<div className="badge-group">
					{persons.map((person, index) => (
						<span key={person.id || index} className="me-1">
							<PersonModalManager>
								{(handleClick) => (
									<span
										className="badge bg-info clickable-badge"
										onClick={() => handleClick(person)}
										id={id + "-" + index}
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
	},

	contacts: (item, view = false, accessKey, id) => {
		return renderFunctions._persons(item, view, accessKey, id, "contacts");
	},

	interviewers: (item, view = false, accessKey, id) => {
		return renderFunctions._persons(item, view, accessKey, id, "interviewers");
	},

	appliedVia: (item, view = false, accessKey, id) => {
		const appliedVia = accessSubAttribute(item, accessKey, "applied_via");
		if (appliedVia === "Aggregator") {
			return renderFunctions.aggregator(item, view, "aggregator", id);
		}
		if (appliedVia) {
			return (
				<span className={"badge bg-info"} id={id}>
					{appliedVia}
				</span>
			);
		}
	},

	aggregator: (item, view = false, accessKey, id) => {
		const aggregator = accessSubAttribute(item, accessKey, "aggregator");
		if (aggregator) {
			return (
				<AggregatorModalManager>
					{(handleClick) => (
						<span
							className={"badge bg-info clickable-badge"}
							onClick={() => handleClick(aggregator)}
							id={id}
						>
							<i className="bi bi-building me-1"></i>
							{aggregator.name}
						</span>
					)}
				</AggregatorModalManager>
			);
		}
	},

	interviewTable: (item, view = false, accessKey) => {
		const interviews = accessSubAttribute(item, accessKey, "interviews");
		return <InterviewsTable data={interviews} jobApplicationId={item.id} />;
	},

	jobApplicationUpdateTable: (item, view = false, accessKey) => {
		const updates = accessSubAttribute(item, accessKey, "updates");
		return <JobApplicationUpdateTable data={updates} jobApplicationId={item.id} />;
	},

	locationMap: (item) => {
		return <LocationMap locations={item ? [item] : []} />;
	},
};

export const renderFieldValue = (field, item, id) => {
	const noText = <span className="text-muted">Not Provided</span>;

	let rendered;
	if (field.render) {
		rendered = field.render(item, false, field.accessKey, id + "-" + field.key);
	} else {
		rendered = item[field.key];
	}
	if (rendered !== null && rendered !== undefined) {
		// allow for 0
		return rendered;
	} else {
		return noText;
	}
};

export const getTableIcon = (title) => {
	const iconMap = {
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
