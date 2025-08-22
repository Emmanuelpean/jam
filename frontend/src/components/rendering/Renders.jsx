import React, { useState } from "react";
import { LocationViewModal } from "../modals/LocationModal";
import { CompanyViewModal } from "../modals/CompanyModal";
import { PersonViewModal } from "../modals/PersonModal";
import { KeywordViewModal } from "../modals/KeywordModal";
import { JobApplicationViewModal } from "../modals/JobApplicationModal";
import { AggregatorViewModal } from "../modals/AggregatorModal";
import { JobViewModal } from "../modals/_JobModal";
import { accessAttribute } from "../../utils/Utils";
import { filesApi } from "../../services/Api";
import { useAuth } from "../../contexts/AuthContext";
import InterviewsTable from "../tables/InterviewTable";
import JobApplicationUpdateTable from "../tables/JobApplicationUpdateTable";
import { THEMES } from "../../utils/Theme";
import { type } from "@testing-library/user-event/dist/type";
import { useGlobalToast } from "../../hooks/useNotificationToast";
import LocationMap from "../maps/LocationMap";

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

// File badge component for downloadable files
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

export const renderFunctions = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	_longText: (item, view = false, key = "description") => {
		const description = accessAttribute(item, key);
		if (description) {
			if (view) {
				return description;
			} else {
				const words = description.split(" ");
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

	note: (item, view = false, key = "note") => {
		return renderFunctions._longText(item, view, key);
	},

	description: (item, view = false, key = "description") => {
		return renderFunctions._longText(item, view, key);
	},

	url: (item, view = false, key = "url") => {
		const url = accessAttribute(item, key);
		if (url) {
			const safeUrl = ensureHttpPrefix(url);
			return (
				<a href={safeUrl} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					{safeUrl.slice(8)} <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
	},

	appTheme: (item, view = false, key = "theme") => {
		const themeKey = accessAttribute(item, key);
		if (themeKey) {
			return THEMES.find((theme) => theme.key === themeKey).name;
		}
	},

	_datetime: (date) => {
		if (date) {
			return new Date(date).toLocaleDateString();
		}
	},

	lastLogin: (item, view = false, key = "last_login") => {
		const date = accessAttribute(item, key);
		return renderFunctions._datetime(date);
	},

	createdDate: (item, view = false, key = "created_at") => {
		const date = accessAttribute(item, key);
		return renderFunctions._datetime(date);
	},

	modifiedDate: (item, view = false, key = "modified_at") => {
		const date = accessAttribute(item, key);
		return renderFunctions._datetime(date);
	},

	datetime: (item, view = false, key = "date") => {
		const date = accessAttribute(item, key);
		return (
			new Date(date).toLocaleDateString() +
			" " +
			new Date(date).toLocaleTimeString([], {
				hour: "2-digit",
				minute: "2-digit",
			})
		);
	},

	date: (item, view = false, key = "date") => {
		const date = accessAttribute(item, key);
		return renderFunctions._datetime(date);
	},

	email: (item, view = false, key = "email") => {
		const email = accessAttribute(item, key);
		if (email)
			return (
				<a href={`mailto:${email}`} className="text-decoration-none">
					<i className="bi bi-envelope me-1"></i>
					{email}
				</a>
			);
	},

	phone: (item, view = false, key = "phone") => {
		const phone = accessAttribute(item, key);
		if (phone) {
			return (
				<a href={`tel:${phone}`} className="text-decoration-none">
					<i className="bi bi-telephone me-1"></i>
					{phone}
				</a>
			);
		}
	},

	linkedinUrl: (item, view = false, key = "linkedin_url") => {
		const url = accessAttribute(item, key);
		if (url) {
			return (
				<a href={url} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					<i className="bi bi-linkedin me-1"></i>
					Profile <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
	},

	isAdmin: (item, view = false, key = "is_admin") => {
		const isAdmin = accessAttribute(item, key);
		return isAdmin ? (
			<i className="bi bi-check-circle-fill text-success"></i>
		) : (
			<i className="bi bi-x-circle-fill text-danger"></i>
		);
	},

	updateType: (item, view = false, key = "type") => {
		const type = accessAttribute(item, key);
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

	salaryRange: (item) => {
		if (!item.salary_min && !item.salary_max) {
			return null;
		}
		if (item.salary_min === item.salary_max) {
			return `£${item.salary_min.toLocaleString()}`;
		}
		if (item.salary_min && item.salary_max) {
			return `£${item.salary_min.toLocaleString()} - £${item.salary_max.toLocaleString()}`;
		}
		if (item.salary_min) return `From £${item.salary_min.toLocaleString()}`;
		if (item.salary_max) return `Up to £${item.salary_max.toLocaleString()}`;
	},

	personalRating: (item, view = false, key = "personal_rating") => {
		const personal_rating = accessAttribute(item, key);
		if (personal_rating) {
			const rating = Math.max(0, Math.min(5, personal_rating));
			const filledStars = Math.floor(rating);
			const emptyStars = 5 - filledStars;
			return (
				<div>
					{"★".repeat(filledStars)}
					{"☆".repeat(emptyStars)}
				</div>
			);
		}
	},

	attendanceType: (item, view = false, key = "attendance_type") => {
		const attendance_type = accessAttribute(item, key);
		if (attendance_type) {
			return attendance_type.charAt(0).toUpperCase() + attendance_type.slice(1);
		}
	},

	status: (item, view = false, key = "status") => {
		const status = accessAttribute(item, key);
		return <span className={`badge ${getApplicationStatusBadgeClass(status)} badge`}>{status}</span>;
	},

	interviewCount: (item, view = false, key = "interviews") => {
		const interviews = accessAttribute(item, key);
		return interviews.length;
	},

	updateCount: (item, view = false, key = "updates") => {
		const updates = accessAttribute(item, key);
		return updates.length;
	},

	// --------------------------------------------------- FILE BADGES -------------------------------------------------

	files: (item) => {
		const cv = accessAttribute(item, "cv");
		const coverLetter = accessAttribute(item, "cover_letter");

		if (!cv && !coverLetter) return null;

		return (
			<div>
				{cv && <FileBadge file={cv} icon="bi bi-file-text" label="CV" />}
				{coverLetter && <FileBadge file={coverLetter} icon="bi bi-file-text" label="Cover Letter" />}
			</div>
		);
	},

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	jobApplication: (item, view = false, key = "job_application", id) => {
		const job_application = accessAttribute(item, key);
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

	job: (item, view = false, key = "job", id) => {
		const job = accessAttribute(item, key);
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

	jobName: (item, view = false, key = "job", id) => {
		const job = accessAttribute(item, key);
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

	keywords: (item, view = false, key = "keywords", id) => {
		const keywords = accessAttribute(item, key);
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

	location: (item, view = false, key = "location", id) => {
		const location = accessAttribute(item, key);
		if (location) {
			return (
				<LocationModalManager>
					{(handleClick) => (
						<span
							className={`badge bg-warning clickable-badge`}
							onClick={() => handleClick(location)}
							id={id}
						>
							<i className="bi bi-geo-alt me-1"></i>
							{location.name}
						</span>
					)}
				</LocationModalManager>
			);
		}
	},

	company: (item, view = false, key = "company", id) => {
		const company = accessAttribute(item, key);
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

	contacts: (item, view = false, key = "contacts", id) => {
		const contacts = accessAttribute(item, key);
		if (contacts && contacts.length > 0) {
			return (
				<div className="badge-group">
					{contacts.map((person, index) => (
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

	appliedVia: (item, view = false, key = "applied_via", id) => {
		const appliedVia = accessAttribute(item, key);
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

	aggregator: (item, view = false, key = "aggregator", id) => {
		const aggregator = accessAttribute(item, key);
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

	interviewTable: (item, view = false, key = "interviews") => {
		const interviews = accessAttribute(item, key);
		return <InterviewsTable interviews={interviews} jobApplicationId={item.id} />;
	},

	jobApplicationUpdateTable: (item, view = false, key = "updates") => {
		const updates = accessAttribute(item, key);
		return <JobApplicationUpdateTable jobApplicationUpdates={updates} jobApplicationId={item.id} />;
	},

	locationMap: (item) => {
		return <LocationMap locations={item ? [item] : []} />;
	},
};

export const renderFieldValue = (field, item, id) => {
	const noText = <span className="text-muted">Not Provided</span>;

	if (field.accessKey) {
		item = accessAttribute(item, field.accessKey);
	}

	if (field.type === "custom" && field.render) {
		return field.render(item);
	}

	if (field.type === "table" && field.render) {
		return field.render();
	}

	let rendered;
	if (field.render) {
		rendered = field.render(item, false, field.key, id + "-" + field.key);
	} else {
		rendered = item[field.key];
	}
	if (rendered !== null && rendered !== undefined) {
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
