import React from "react";
import GenericModal from "../GenericModal";
import { renderFunctions } from "../Renders";

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

const JobViewModal = ({ show, onHide, job, onEdit, size }) => {
	if (!job) return null;

	// Define the fields to display in the view modal
	const viewFields = [
		{
			name: "title",
			label: "Job Title",
			type: "text",
			render: () => renderFunctions.title(job),
		},
		{
			name: "company_name",
			label: "Company",
			type: "text",
		},
		{
			name: "location_display",
			label: "Location",
			type: "text",
		},
		{
			name: "description",
			label: "Job Description",
			type: "textarea",
			render: () => renderFunctions.description(job),
		},
		{
			name: "salary_range",
			label: "Salary Range",
			type: "text",
			render: () => renderFunctions.salaryRange(job),
		},
		{
			name: "personal_rating",
			label: "Personal Rating",
			type: "text",
			render: () => (
				<div>
					{renderFunctions.personalRating(job)}
					{job.personal_rating !== null && job.personal_rating !== undefined && (
						<span className="ms-2 text-muted">({job.personal_rating}/5)</span>
					)}
				</div>
			),
		},
		{
			name: "url",
			label: "Job URL",
			type: "url",
			render: () => renderFunctions.url(job),
		},
		{
			name: "notes",
			label: "Notes",
			type: "textarea",
			render: () => (
				<div style={{ maxWidth: "100%", whiteSpace: "pre-wrap" }}>
					{job.notes || <span className="text-muted">No notes</span>}
				</div>
			),
		},
	];

	// Transform job data for display (keeping fallback values for fields not using render functions)
	const displayData = {
		...job,
		company_name: job.company_name || "Unknown Company",
		location_display: job.location_city
			? `${job.location_city}, ${job.location_country}${job.location_remote ? " (Remote)" : ""}`
			: "Unknown Location",
	};

	// Custom content for additional job information
	const customContent = (
		<div className="mt-4">
			{job.url && (
				<div className="alert alert-info">
					<i className="bi bi-link-45deg me-2"></i>
					<strong>Job Link:</strong>{" "}
					<a href={job.url} target="_blank" rel="noopener noreferrer" className="alert-link">
						View Original Job Posting <i className="bi bi-box-arrow-up-right ms-1"></i>
					</a>
				</div>
			)}

			{job.status && (
				<div className="row">
					<div className="col-12">
						<div className="card bg-light">
							<div className="card-body text-center">
								<h6 className="card-title mb-2">Application Status</h6>
								{/*{renderFunctions.statusBadge({ ...job, status: job.status })}*/}
							</div>
						</div>
					</div>
				</div>
			)}
		</div>
	);

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Job Application"
			size={size}
			data={displayData}
			viewFields={viewFields}
			onEdit={onEdit}
			customContent={customContent}
		/>
	);
};

export default JobViewModal;
