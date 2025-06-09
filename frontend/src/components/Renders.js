import React, { useState } from "react";
import LocationViewModal from "./modals/LocationViewModal";
import CompanyViewModal from "./modals/CompanyViewModal";
import PersonViewModal from "./modals/PersonViewModal";
import KeywordViewModal from "./modals/KeywordViewModal";

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
const JobApplicationModalManager = createModalManager(KeywordViewModal, "jobApplication"); // TODO to change

// Helper function to get status badge class
const getApplicationStatusBadgeClass = (status) => {
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

export const renderFunctions = {
	// ------------------------------------------------------ TEXT -----------------------------------------------------

	name: (item, view = false) => {
		// TODO see if the first column can be bolden instead
		if (!item.name) {
			return view ? <span className="text-muted">No name provided</span> : null;
		} else {
			if (view) {
				return <div>{item.name}</div>;
			} else {
				return <strong>{item.name}</strong>;
			}
		}
	},

	title: (item, view = false) => {
		if (!item.title) {
			return view ? <span className="text-muted">No title provided</span> : null;
		} else {
			if (view) {
				return <div>{item.title}</div>;
			} else {
				return <strong>{item.title}</strong>;
			}
		}
	},

	_longText: (item, noText, view = false) => {
		if (!item.description) {
			return view ? <span className="text-muted">{noText}</span> : null;
		} else {
			if (view) {
				return item.description;
			} else {
				const words = item.description.split(" ");
				const truncated = words.slice(0, 12).join(" ");
				const needsEllipsis = words.length > 12;

				return (
					<div style={{ maxWidth: "500px", overflow: "hidden", textOverflow: "ellipsis" }}>
						{truncated}
						{needsEllipsis ? "..." : ""}
					</div>
				);
			}
		}
	},

	note: (item, view = false) => {
		return renderFunctions._longText(item, "No note provided", view);
	},

	description: (item, view = false) => {
		return renderFunctions._longText(item, "No description provided", view);
	},

	url: (item, view = false) => {
		if (!item.url) {
			return view ? <span className="text-muted">No URL provided</span> : null;
		} else {
			return (
				<a href={item.url} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					Visit Website <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
	},

	createdDate: (item) => new Date(item.created_at).toLocaleDateString(),

	email: (item, view = false) => {
		if (!item.email) {
			return view ? <span className="text-muted">No email address provided</span> : null;
		} else {
			return (
				<a href={`mailto:${item.email}`} className="text-decoration-none">
					<i className="bi bi-envelope me-1"></i>
					{item.email}
				</a>
			);
		}
	},

	phone: (item, view = false) => {
		if (!item.phone) {
			return view ? <span className="text-muted">No phone number provided</span> : null;
		} else {
			return (
				<a href={`tel:${item.phone}`} className="text-decoration-none">
					<i className="bi bi-telephone me-1"></i>
					{item.phone}
				</a>
			);
		}
	},

	linkedinUrl: (item, view = false) => {
		if (!item.linkedin_url) {
			return view ? <span className="text-muted">No LinkedIn profile provided</span> : null;
		} else {
			return (
				<a href={item.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					<i className="bi bi-linkedin me-1"></i>
					Profile <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			);
		}
	},

	salaryRange: (item, view = false) => {
		if (!item.salary_min && !item.salary_max) {
			return view ? <span className="text-muted">No salary provided</span> : null;
		} else if (item.salary_min === item.salary_max) {
			return `£${item.salary_min.toLocaleString()}`;
		} else if (item.salary_min && item.salary_max) {
			return `£${item.salary_min.toLocaleString()} - £${item.salary_max.toLocaleString()}`;
		} else if (item.salary_min) return `From £${item.salary_min.toLocaleString()}`;
		else if (item.salary_max) return `Up to £${item.salary_max.toLocaleString()}`;
	},

	personalRating: (item, view = false) => {
		if (!item.personal_rating) {
			return view ? <span className="text-muted">No rating provided</span> : null;
		} else {
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

	// ----------------------------------------------------- BADGES ----------------------------------------------------

	jobApplication: (item, view = false) => {
		if (!item.job_application) {
			return view ? <span className="text-muted">No status provided</span> : null;
		} else {
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

	keywords: (item, view = false) => {
		if (!item.keywords || item.keywords.length === 0) {
			return view ? <span className="text-muted">No keywords provided</span> : null;
		} else {
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

	location: (item, view = false) => {
		if (!item.location) {
			return view ? <span className="text-muted">No location provided</span> : null;
		} else {
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

	company: (item, view = false) => {
		if (!item.company) {
			return view ? <span className="text-muted">No company provided</span> : null;
		} else {
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

	persons: (item, view = false) => {
		if (!item.persons || item.persons.length === 0) {
			return view ? <span className="text-muted">No persons provided</span> : null;
		} else {
			return (
				<div>
					{item.persons.map((person, index) => (
						<span key={person.id || index} className="me-1">
							<PersonModalManager>
								{(handleClick) => (
									<span
										className={"badge bg-info clickable-badge"}
										onClick={() => handleClick(item.name)}
									>
										<i className="bi bi-file-person me-1"></i>
										{item.name}
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

// Accessor functions for sorting and searching
export const accessorFunctions = {
	// TODO to replace with sorting function
	personName: (person) => `${person.first_name} ${person.last_name}`,

	salaryRange: (job) => {
		if (!job.salary_min && !job.salary_max) return "";
		if (job.salary_min && job.salary_max) {
			return `£${job.salary_min.toLocaleString()} - £${job.salary_max.toLocaleString()}`;
		}
		if (job.salary_min) return `From £${job.salary_min.toLocaleString()}`;
		if (job.salary_max) return `Up to £${job.salary_max.toLocaleString()}`;
		return "";
	},

	jobTitle: (item) => item.job?.title || "",

	keywords: (item) => item.keywords?.map((k) => k.name).join(", ") || "",
};
