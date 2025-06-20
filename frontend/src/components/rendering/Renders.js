import React, { useState } from "react";
import LocationViewModal from "../modals/location/LocationViewModal";
import CompanyViewModal from "../modals/company/CompanyViewModal";
import PersonViewModal from "../modals/person/PersonViewModal";
import KeywordViewModal from "../modals/keyword/KeywordViewModal";
import JobApplicationViewModal from "../modals/job_application/JobApplicationViewModal";
import JobViewModal from "../modals/job/JobViewModal";

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

// Create specific modal managers
const LocationModalManager = createModalManager(LocationViewModal, "location");
const CompanyModalManager = createModalManager(CompanyViewModal, "company");
const PersonModalManager = createModalManager(PersonViewModal, "person");
const KeywordModalManager = createModalManager(KeywordViewModal, "keywords");
const JobApplicationModalManager = createModalManager(JobApplicationViewModal, "jobApplication");
const JobModalManager = createModalManager(JobViewModal, "job");

// Helper function to get status badge class
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

	_longText: (item, view = false) => {
		if (item.description) {
			if (view) {
				return item.description;
			} else {
				const words = item.description.split(" ");
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

	note: (item, view = false) => {
		return renderFunctions._longText(item, view);
	},

	description: (item, view = false) => {
		return renderFunctions._longText(item, view);
	},

	_url: (item) => {
		if (item.url) {
			const safeUrl = ensureHttpPrefix(item.url);
			return (
				<a href={safeUrl} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					Visit Website <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
	},
	url: (item, view = false) => {
		return renderFunctions._url(item, view);
	},

	datetime: (date) => {
		if (date) {
			return new Date(date).toLocaleDateString();
		}
	},

	createdDate: (item) => {
		return renderFunctions.datetime(item.created_at);
	},

	modifiedDate: (item) => {
		return renderFunctions.datetime(item.modified_at)
	},

	date: (item) => {
		return renderFunctions.datetime(item.date);
	},

	email: (item) => {
		if (item.email)
			return (
				<a href={`mailto:${item.email}`} className="text-decoration-none">
					<i className="bi bi-envelope me-1"></i>
					{item.email}
				</a>
			);
	},

	phone: (item) => {
		if (item.phone) {
			return (
				<a href={`tel:${item.phone}`} className="text-decoration-none">
					<i className="bi bi-telephone me-1"></i>
					{item.phone}
				</a>
			);
		}
	},

	linkedinUrl: (item) => {
		if (item.linkedin_url) {
			return (
				<a href={item.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
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

	personalRating: (item) => {
		if (item.personal_rating) {
			const rating = Math.max(0, Math.min(5, item.personal_rating));
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

	status: (item) => {
		return (
			<span
				className={`badge ${getApplicationStatusBadgeClass(item.status)} badge`}
			>
            {item.status}
        </span>
		);
	},

	interviewCount: (item) => {
		return item.interviews?.length || 0
	},

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	jobApplication: (item) => {
		if (item.job_application) {
			return (
				<JobApplicationModalManager>
					{(handleClick) => (
						<span
							className={`badge ${getApplicationStatusBadgeClass(item.job_application.status)} clickable-badge`}
							onClick={() => handleClick(item.job_application)}
						>
							{item.job_application.status}
						</span>
					)}
				</JobApplicationModalManager>
			);
		}
	},

	job: (item) => {
		if (item.job) {
			return (
				<JobModalManager>
					{(handleClick) => (
						<span
							className={`badge bg-info clickable-badge`}
							onClick={() => handleClick(item.job)}
						>
                        <i className="bi bi-briefcase me-1"></i>
							{item.job.title}
                    </span>
					)}
				</JobModalManager>
			);
		}
	},

	keywords: (item) => {
		if (item.keywords && item.keywords.length > 0) {
			return (
				<div>
					{item.keywords.map((keyword, index) => (
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

	location: (item) => {
		if (item.location) {
			return (
				<LocationModalManager>
					{(handleClick) => (
						<span className={`badge bg-primary clickable-badge`} onClick={() => handleClick(item.location)}>
							<i className="bi bi-geo-alt me-1"></i>
							{item.location.name}
						</span>
					)}
				</LocationModalManager>
			);
		}
	},

	company: (item) => {
		if (item.company) {
			return (
				<CompanyModalManager>
					{(handleClick) => (
						<span className={"badge bg-info clickable-badge"} onClick={() => handleClick(item.company)}>
							<i className="bi bi-building me-1"></i>
							{item.company.name}
						</span>
					)}
				</CompanyModalManager>
			);
		}
	},

	contacts: (item, key="contacts") => {
		const cont = item[key]
		if (cont && cont.length > 0) {
			return (
				<div>
					{cont.map((person, index) => (
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
