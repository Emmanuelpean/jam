import React, { useState } from "react";

import LocationViewModal from "../modals/LocationViewModal";
import CompanyViewModal from "../modals/CompanyViewModal";

// Generic modal manager factory
const createModalManager = (ModalComponent, modalProp, sizeProp = "lg") => {
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
			size: sizeProp,
			[modalProp]: selectedItem,
			showEditButton: true,
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
const LocationModalManager = createModalManager(LocationViewModal, "location", "lg");
const CompanyModalManager = createModalManager(CompanyViewModal, "company", "lg");

// Reusable column definitions that can be used across different tables
export const columns = {
	// ------------------------------------------------- GENERAL NAMES -------------------------------------------------

	// Simple name column
	name: {
		key: "name",
		label: "name",
		sortable: true,
		searchable: true,
		type: "text",
		render: (item) => <strong>{item.name}</strong>,
	},

	// Simple title column
	title: {
		key: "title",
		label: "Job Title",
		sortable: true,
		searchable: true,
		type: "text",
		render: (job) => <strong>{job.title}</strong>,
	},

	// Description column
	description: {
		key: "description",
		label: "Description",
		sortable: false,
		searchable: true,
		type: "text",
		render: (item) => {
			const description = item.description || "No description";
			const firstSentence = description.match(/^[^.!?]*[.!?]/)?.[0] || description;
			return (
				<div style={{ maxWidth: "600px", overflow: "hidden", textOverflow: "ellipsis" }}>{firstSentence}</div>
			);
		},
	},

	// URL/Website column
	url: {
		key: "url",
		label: "Website",
		sortable: false,
		searchable: true,
		type: "text",
		render: (item) =>
			item.url ? (
				<a href={item.url} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					Visit Website <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			) : null,
	},

	// Created date column - common across all entities
	createdAt: {
		key: "created_at",
		label: "Date Added",
		type: "date",
		sortable: true,
		searchable: false,
		render: (item) => new Date(item.created_at).toLocaleDateString(),
	},

	// ---------------------------------------------------- LOCATION ---------------------------------------------------

	// Location column with built-in modal handling
	location: {
		key: "location",
		label: "Location",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "location.name",
		searchFields: ["location.name"],
		accessor: (item) => {
			const loc = item.location;
			if (!loc) return "";
			return loc.name;
		},
		render: (item) => {
			const loc = item.location;
			if (!loc) return <span className="text-muted">No location</span>;

			return (
				<LocationModalManager>
					{(handleLocationClick) => (
						<span
							className={`badge ${loc.remote ? "bg-success" : "bg-primary"} clickable-badge`}
							onClick={() => handleLocationClick(loc)}
							style={{ cursor: "pointer" }}
							title="Click to view location details"
						>
							<i className="bi bi-geo-alt me-1"></i>
							{loc.name}
						</span>
					)}
				</LocationModalManager>
			);
		},
	},

	// City column for location table
	city: {
		key: "city",
		label: "City",
		sortable: true,
		searchable: true,
		type: "text",
	},

	// Postcode column for location table
	postcode: {
		key: "postcode",
		label: "Postcode",
		sortable: true,
		searchable: true,
		type: "text",
	},

	// Country column for location table
	country: {
		key: "country",
		label: "Country",
		sortable: true,
		searchable: true,
		type: "text",
	},

	// --------------------------------------------------- COMPANIES ---------------------------------------------------

	// Company column with built-in modal handling
	company: {
		key: "company",
		label: "Company",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "company.name",
		searchFields: ["company.name"],
		accessor: (item) => item.company?.name || "",
		render: (item) => {
			const company = item.company;
			if (!company) return <span className="text-muted">No company</span>;

			return (
				<CompanyModalManager>
					{(handleCompanyClick) => (
						<span
							className="badge bg-info clickable-badge"
							onClick={() => handleCompanyClick(company)}
							style={{ cursor: "pointer" }}
							title="Click to view company details"
						>
							<i className="bi bi-building me-1"></i>
							{company.name}
						</span>
					)}
				</CompanyModalManager>
			);
		},
	},

	// ---------------------------------------------------- PERSONS ----------------------------------------------------

	// Person full name column
	personName: {
		key: "name",
		label: "name",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "last_name",
		accessor: (person) => `${person.first_name} ${person.last_name}`,
		render: (person) => <strong>{`${person.first_name} ${person.last_name}`}</strong>,
	},

	// Email column
	email: {
		key: "email",
		label: "Email",
		sortable: true,
		searchable: true,
		type: "text",
		render: (item) =>
			item.email ? (
				<a href={`mailto:${item.email}`} className="text-decoration-none">
					<i className="bi bi-envelope me-1"></i>
					{item.email}
				</a>
			) : null,
	},

	// Phone column
	phone: {
		key: "phone",
		label: "Phone",
		sortable: false,
		searchable: true,
		type: "text",
		render: (item) =>
			item.phone ? (
				<a href={`tel:${item.phone}`} className="text-decoration-none">
					<i className="bi bi-telephone me-1"></i>
					{item.phone}
				</a>
			) : null,
	},

	// LinkedIn URL column - for people
	linkedinUrl: {
		key: "linkedin_url",
		label: "LinkedIn",
		sortable: false,
		searchable: true,
		type: "text",
		render: (item) =>
			item.linkedin_url ? (
				<a href={item.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
					<i className="bi bi-linkedin me-1"></i>
					Profile <i className="bi bi-box-arrow-up-right ms-1"></i>
				</a>
			) : null,
	},

	// ------------------------------------------------------ JOBS -----------------------------------------------------

	// Salary range column - for jobs
	salaryRange: {
		key: "salary_range",
		label: "Salary",
		sortable: true,
		searchable: false,
		type: "text",
		sortField: "salary_min",
		accessor: (job) => {
			if (!job.salary_min && !job.salary_max) return "";
			if (job.salary_min && job.salary_max) {
				return `£${job.salary_min.toLocaleString()} - £${job.salary_max.toLocaleString()}`;
			}
			if (job.salary_min) return `From £${job.salary_min.toLocaleString()}`;
			if (job.salary_max) return `Up to £${job.salary_max.toLocaleString()}`;
			return "";
		},
		render: (job) => {
			if (!job.salary_min && !job.salary_max) {
				return <span className="text-muted">Not specified</span>;
			}
			if (job.salary_min && job.salary_max) {
				return `£${job.salary_min.toLocaleString()} - £${job.salary_max.toLocaleString()}`;
			}
			if (job.salary_min) return `From £${job.salary_min.toLocaleString()}`;
			if (job.salary_max) return `Up to £${job.salary_max.toLocaleString()}`;
			return "";
		},
	},

	// Personal rating column - for jobs
	personalRating: {
		key: "personal_rating",
		label: "Rating",
		sortable: true,
		type: "number",
		render: (job) => {
			// Check if rating is null or undefined
			if (job.personal_rating === null || job.personal_rating === undefined) {
				return "/";
			}

			const rating = Math.max(0, Math.min(5, job.personal_rating)); // Clamp between 0 and 5
			const filledStars = Math.floor(rating);
			const emptyStars = 5 - filledStars;

			return (
				<div>
					{"★".repeat(filledStars)}
					{"☆".repeat(emptyStars)}
				</div>
			);
		},
	},

	// Job reference column - for applications, interviews
	jobReference: {
		key: "job_title",
		label: "Job",
		sortable: true,
		searchable: true,
		type: "text",
		sortField: "job.title",
		searchFields: ["job.title", "job.company.name"],
		accessor: (item) => item.job?.title || "",
		render: (item) => {
			if (!item.job) return "No job";
			return (
				<div>
					<strong>{item.job.title}</strong>
					{item.job.company && <div className="small text-muted">at {item.job.company.name}</div>}
				</div>
			);
		},
	},

	// Note column - for applications, interviews
	note: {
		key: "note",
		label: "Notes",
		sortable: false,
		searchable: true,
		type: "text",
		render: (item) => (
			<div style={{ maxWidth: "250px", overflow: "hidden", textOverflow: "ellipsis" }}>
				{item.note || <span className="text-muted">No notes</span>}
			</div>
		),
	},

	// Keywords column - can be used in Jobs
	keywords: {
		key: "keywords",
		label: "Keywords",
		sortable: false,
		searchable: true,
		type: "text",
		searchFields: ["keywords.name"],
		accessor: (item) => item.keywords?.map((k) => k.name).join(", ") || "",
		render: (item) => {
			if (!item.keywords || item.keywords.length === 0) {
				return <span className="text-muted">No keywords</span>;
			}
			return (
				<div>
					{item.keywords.map((keyword, index) => (
						<span key={keyword.id} className="badge bg-secondary me-1 mb-1">
							{keyword.name}
						</span>
					))}
				</div>
			);
		},
	},
};
