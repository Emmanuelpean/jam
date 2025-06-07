import React from "react";
import GenericModal from "../GenericModal";

const PersonViewModal = ({ show, onHide, person, onEdit, size }) => {
	if (!person) return null;

	// Define the fields to display in the view modal
	const viewFields = [
		{
			name: "full_name",
			label: "Full Name",
			type: "text",
		},
		{
			name: "company_name",
			label: "Company",
			type: "text",
		},
		{
			name: "email",
			label: "Email",
			type: "email",
		},
		{
			name: "phone",
			label: "Phone",
			type: "text",
		},
		{
			name: "linkedin_url",
			label: "LinkedIn Profile",
			type: "url",
		},
	];

	// Transform person data for display
	const displayData = {
		...person,
		full_name: `${person.first_name} ${person.last_name}`,
		company_name: person.company?.name || "No company assigned",
		email: person.email || "No email provided",
		phone: person.phone || "No phone provided",
		linkedin_url: person.linkedin_url || "No LinkedIn profile",
	};

	// Custom content for additional person information
	const customContent = (
		<div className="mt-4">
			{/* Contact Information Card */}
			<div className="row">
				<div className="col-12">
					<div className="card bg-light">
						<div className="card-body">
							<h6 className="card-title mb-3">
								<i className="bi bi-person-badge me-2"></i>
								Contact Information
							</h6>
							<div className="row">
								{person.email && (
									<div className="col-md-6 mb-2">
										<small className="text-muted d-block">Email</small>
										<a href={`mailto:${person.email}`} className="text-decoration-none">
											<i className="bi bi-envelope me-1"></i>
											{person.email}
										</a>
									</div>
								)}
								{person.phone && (
									<div className="col-md-6 mb-2">
										<small className="text-muted d-block">Phone</small>
										<a href={`tel:${person.phone}`} className="text-decoration-none">
											<i className="bi bi-telephone me-1"></i>
											{person.phone}
										</a>
									</div>
								)}
								{person.linkedin_url && (
									<div className="col-12 mb-2">
										<small className="text-muted d-block">LinkedIn</small>
										<a
											href={person.linkedin_url}
											target="_blank"
											rel="noopener noreferrer"
											className="text-decoration-none"
										>
											<i className="bi bi-linkedin me-1"></i>
											View LinkedIn Profile
											<i className="bi bi-box-arrow-up-right ms-1"></i>
										</a>
									</div>
								)}
							</div>
						</div>
					</div>
				</div>
			</div>

			{/* Company Information */}
			{person.company && (
				<div className="row mt-3">
					<div className="col-12">
						<div className="alert alert-info">
							<i className="bi bi-building me-2"></i>
							<strong>Works at:</strong> {person.company.name}
							{person.company.url && (
								<>
									{" - "}
									<a
										href={person.company.url}
										target="_blank"
										rel="noopener noreferrer"
										className="alert-link"
									>
										Visit Company Website
										<i className="bi bi-box-arrow-up-right ms-1"></i>
									</a>
								</>
							)}
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
			title="Person Details"
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

export default PersonViewModal;