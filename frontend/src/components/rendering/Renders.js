import React, { useState } from "react";
import LocationViewModal from "../modals/location/LocationViewModal";
import CompanyViewModal from "../modals/company/CompanyViewModal";
import PersonViewModal from "../modals/person/PersonViewModal";
import KeywordViewModal from "../modals/keyword/KeywordViewModal";
import JobApplicationViewModal from "../modals/job_application/JobApplicationViewModal";
import JobViewModal from "../modals/job/JobViewModal";
import { accessAttribute } from "../../utils/Utils";

const createModalManager = (ModalComponent, modalProp) => {
	return ({ children, onEdit }) => {
		const [showModal, setShowModal] = useState(false);
		const [selectedItem, setSelectedItem] = useState(null);

		const handleItemClick = (item) => {
			setSelectedItem(item);
			setShowModal(true);
		};

		const closeModal = () => {
			setShowModal(false);
			// Delay clearing the selected item to allow closing animation
			setTimeout(() => {
				setSelectedItem(null);
			}, 300); // Bootstrap modal animation duration is typically 300ms
		};

		const handleEdit = () => {
			if (onEdit && selectedItem) {
				onEdit(selectedItem);
				closeModal();
			}
		};

		const modalProps = {
			show: showModal,
			onHide: closeModal,
			[modalProp]: selectedItem,
			showEditButton: false, // Remove edit button from view modals
			onEdit: handleEdit,
		};

		return (
			<>
				{children(handleItemClick)}
				<ModalComponent {...modalProps} />
			</>
		);
	};
};

const LocationModalManager = createModalManager(LocationViewModal, "location");
const CompanyModalManager = createModalManager(CompanyViewModal, "company");
const PersonModalManager = createModalManager(PersonViewModal, "person");
const KeywordModalManager = createModalManager(KeywordViewModal, "keywords");
const JobApplicationModalManager = createModalManager(JobApplicationViewModal, "jobApplication");
const JobModalManager = createModalManager(JobViewModal, "job");

export const getApplicationStatusBadgeClass = (status) => {
	switch (status?.toLowerCase()) {
		case "applied":
			return "bg-primary";
		case "interview":
			return "bg-warning text-dark";
		case "offer":
			return "bg-success";
		case "rejected":
			return "bg-danger";
		case "withdrawn":
			return "bg-secondary";
		default:
			return "bg-light text-dark";
	}
};

const ensureHttpPrefix = (url) => {
	if (!url) return url;
	if (url.match(/^https?:\/\//)) return url;
	return `https://${url}`;
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

	note: (item, view = false, key = "description") => {
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
					Visit Website <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
	},

	_datetime: (date) => {
		if (date) {
			return new Date(date).toLocaleDateString();
		}
	},

	createdDate: (item, view = false, key = "created_at") => {
		const date = accessAttribute(item, key);
		return renderFunctions._datetime(date);
	},

	modifiedDate: (item, view = false, key = "modified_at") => {
		const date = accessAttribute(item, key);
		return renderFunctions._datetime(date);
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

	status: (item, view = false, key = "status") => {
		const status = accessAttribute(item, key);
		return <span className={`badge ${getApplicationStatusBadgeClass(status)} badge`}>{status}</span>;
	},

	interviewCount: (item, view = false, key = "interviews") => {
		const interviews = accessAttribute(item, key);
		return interviews?.length || 0;
	},

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	jobApplication: (item, view = false, key = "job_application") => {
		const job_application = accessAttribute(item, key);
		if (job_application) {
			return (
				<JobApplicationModalManager>
					{(handleClick) => (
						<span
							className={`badge ${getApplicationStatusBadgeClass(job_application.status)} clickable-badge`}
							onClick={() => handleClick(job_application)}
						>
							{job_application.status}
						</span>
					)}
				</JobApplicationModalManager>
			);
		}
	},

	job: (item, view = false, key = "job") => {
		const job = accessAttribute(item, key);
		if (job) {
			return (
				<JobModalManager>
					{(handleClick) => (
						<span className={`badge bg-info clickable-badge`} onClick={() => handleClick(job)}>
							<i className="bi bi-briefcase me-1"></i>
							{job.title}
						</span>
					)}
				</JobModalManager>
			);
		}
	},

	keywords: (item, view = false, key = "keywords") => {
		const keywords = accessAttribute(item, key);
		if (keywords && keywords.length > 0) {
			return (
				<div>
					{keywords.map((keyword, index) => (
						<KeywordModalManager key={keyword.id || index}>
							{(handleClick) => (
								<span
									className="badge bg-info clickable-badge me-1"
									onClick={() => handleClick(keyword)}
								>
									<i className="bi bi-tag me-1"></i>
									{keyword.name}
								</span>
							)}
						</KeywordModalManager>
					))}
				</div>
			);
		}
	},

	location: (item, view = false, key = "location") => {
		const location = accessAttribute(item, key);
		if (location) {
			return (
				<LocationModalManager>
					{(handleClick) => (
						<span className={`badge bg-warning clickable-badge`} onClick={() => handleClick(location)}>
							<i className="bi bi-geo-alt me-1"></i>
							{location.name}
						</span>
					)}
				</LocationModalManager>
			);
		}
	},

	company: (item, view = false, key = "company") => {
		console.log(key);
		const company = accessAttribute(item, key);
		if (company) {
			return (
				<CompanyModalManager>
					{(handleClick) => (
						<span className={"badge bg-info clickable-badge"} onClick={() => handleClick(company)}>
							<i className="bi bi-building me-1"></i>
							{company.name}
						</span>
					)}
				</CompanyModalManager>
			);
		}
	},

	contacts: (item, view = false, key = "contacts") => {
		const contacts = accessAttribute(item, key);
		if (contacts && contacts.length > 0) {
			return (
				<div>
					{contacts.map((person, index) => (
						<span key={person.id || index} className="me-1">
							<PersonModalManager>
								{(handleClick) => (
									<span className="badge bg-info clickable-badge" onClick={() => handleClick(person)}>
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
};

export const renderFieldValue = (field, item) => {
	const noText = <span className="text-muted">Not Provided</span>;
	if (field.accessKey) {
		item = accessAttribute(item, field.accessKey);
	}
	let rendered;
	if (field.render) {
		rendered = field.render(item);
	} else {
		rendered = item[field.key];
	}
	if (rendered) {
		return rendered;
	} else {
		return noText;
	}
};
