import React, { useState } from "react";
import LocationViewModal from "./modals/LocationViewModal";
import CompanyViewModal from "./modals/CompanyViewModal";

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
const LocationModalManager = createModalManager(LocationViewModal, "location", "lg");
const CompanyModalManager = createModalManager(CompanyViewModal, "company", "lg");

// Helper function to get status badge class
const getStatusBadgeClass = (status) => {
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

// Render Functions
export const renderFunctions = {
	// Basic text renderers
	strongText: (item, fieldKey) => <strong>{item[fieldKey]}</strong>,

	jobTitle: (job) => <strong>{job.title}</strong>,

	personName: (person) => <strong>{`${person.first_name} ${person.last_name}`}</strong>,

	// Description with truncation
	description: (item) => {
		const description = item.description || "No description";
		const firstSentence = description.match(/^[^.!?]*[.!?]/)?.[0] || description;
		return <div style={{ maxWidth: "600px", overflow: "hidden", textOverflow: "ellipsis" }}>{firstSentence}</div>;
	},

	// URL/Website links
	websiteUrl: (item) =>
		item.url ? (
			<a href={item.url} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
				Visit Website <i className="bi bi-box-arrow-up-right ms-1"></i>
			</a>
		) : null,

	// Date formatting
	createdDate: (item) => new Date(item.created_at).toLocaleDateString(),

	// Location with modal
	locationBadge: (item) => {
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

	// Company with modal
	companyBadge: (item) => {
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

	// Contact information
	email: (item) =>
		item.email ? (
			<a href={`mailto:${item.email}`} className="text-decoration-none">
				<i className="bi bi-envelope me-1"></i>
				{item.email}
			</a>
		) : null,

	phone: (item) =>
		item.phone ? (
			<a href={`tel:${item.phone}`} className="text-decoration-none">
				<i className="bi bi-telephone me-1"></i>
				{item.phone}
			</a>
		) : null,

	linkedinUrl: (item) =>
		item.linkedin_url ? (
			<a href={item.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-decoration-none">
				<i className="bi bi-linkedin me-1"></i>
				Profile <i className="bi bi-box-arrow-up-right ms-1"></i>
			</a>
		) : null,

	// Job-specific renderers
	salaryRange: (job) => {
		if (!job.salary_min && !job.salary_max) {
			return <span className="text-muted">Not specified</span>;
		}
		if (job.salary_min === job.salary_max) {
			return `£${job.salary_min.toLocaleString()}`;
		}
		if (job.salary_min && job.salary_max) {
			return `£${job.salary_min.toLocaleString()} - £${job.salary_max.toLocaleString()}`;
		}
		if (job.salary_min) return `From £${job.salary_min.toLocaleString()}`;
		if (job.salary_max) return `Up to £${job.salary_max.toLocaleString()}`;
		return "";
	},

	personalRating: (job) => {
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

	jobReference: (item) => {
		if (!item.job) return "No job";
		return (
			<div>
				<strong>{item.job.title}</strong>
				{item.job.company && <div className="small text-muted">at {item.job.company.name}</div>}
			</div>
		);
	},

	// Status badge
	statusBadge: (item) => {
		if (!item.status) return <span className="text-muted">Unknown</span>;

		const status =
			typeof item.status === "string" ? item.status.charAt(0).toUpperCase() + item.status.slice(1) : "Unknown";

		return <span className={`badge ${getStatusBadgeClass(item.status)}`}>{status}</span>;
	},

	// Notes with truncation
	note: (item) => (
		<div style={{ maxWidth: "250px", overflow: "hidden", textOverflow: "ellipsis" }}>
			{item.note || <span className="text-muted">No notes</span>}
		</div>
	),

	// Keywords as badges
	keywords: (item) => {
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
};

// Accessor functions for sorting and searching
export const accessorFunctions = {
	personName: (person) => `${person.first_name} ${person.last_name}`,

	locationName: (item) => {
		const loc = item.location;
		if (!loc) return "";
		return loc.name;
	},

	companyName: (item) => item.company?.name || "",

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
