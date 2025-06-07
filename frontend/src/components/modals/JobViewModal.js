import React from "react";
import GenericModal from "../GenericModal";

const JobViewModal = ({ show, onHide, job, onEdit, size }) => {
	if (!job) return null;

	// Define the fields to display in the view modal
	const viewFields = [
		{
			name: "title",
			label: "Job Title",
			type: "text",
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
			name: "status",
			label: "Status",
			type: "select",
			options: [
				{ value: "applied", label: "Applied" },
				{ value: "interview", label: "Interview" },
				{ value: "offer", label: "Offer" },
				{ value: "rejected", label: "Rejected" },
				{ value: "withdrawn", label: "Withdrawn" },
			],
		},
		{
			name: "description",
			label: "Job Description",
			type: "textarea",
		},
		{
			name: "salary_range",
			label: "Salary Range",
			type: "text",
		},
		{
			name: "personal_rating",
			label: "Personal Rating",
			type: "text",
		},
		{
			name: "url",
			label: "Job URL",
			type: "url",
		},
		{
			name: "notes",
			label: "Notes",
			type: "textarea",
		},
	];

	// Transform job data for display
	const displayData = {
		...job,
		company_name: job.company_name || "Unknown Company",
		location_display: job.location_city
			? `${job.location_city}, ${job.location_country}${job.location_remote ? " (Remote)" : ""}`
			: "Unknown Location",
		salary_range: (() => {
			if (job.salary_min && job.salary_max) {
				return `$${Number(job.salary_min).toLocaleString()} - $${Number(job.salary_max).toLocaleString()}`;
			} else if (job.salary_min) {
				return `From $${Number(job.salary_min).toLocaleString()}`;
			} else if (job.salary_max) {
				return `Up to $${Number(job.salary_max).toLocaleString()}`;
			}
			return "Not specified";
		})(),
		personal_rating: (() => {
			const rating = job.personal_rating || 0;
			return `${"★".repeat(rating)}${"☆".repeat(5 - rating)} (${rating}/5)`;
		})(),
		status:
			job.status && typeof job.status === "string"
				? job.status.charAt(0).toUpperCase() + job.status.slice(1)
				: "Unknown",
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
								<span className={`badge fs-6 ${getStatusBadgeClass(job.status)}`}>
									{job.status && typeof job.status === "string"
										? job.status.charAt(0).toUpperCase() + job.status.slice(1)
										: "Unknown"}
								</span>
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
			showEditButton={true}
			showSystemFields={true}
			customContent={customContent}
		/>
	);
};

// Helper function to get status badge class
const getStatusBadgeClass = (status) => {
	if (!status || typeof status !== "string") return "bg-primary";

	const statusMap = {
		applied: "bg-primary",
		interview: "bg-warning text-dark",
		offer: "bg-success",
		rejected: "bg-danger",
		withdrawn: "bg-secondary",
	};
	return statusMap[status.toLowerCase()] || "bg-primary";
};

export default JobViewModal;
