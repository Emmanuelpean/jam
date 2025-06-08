import React from "react";
import GenericModal from "../GenericModal";
import { renderFunctions } from "../Renders";

const PersonViewModal = ({ show, onHide, person, onEdit, size }) => {
	if (!person) return null;

	// Define the fields to display in the view modal
	const viewFields = [
		{
			name: "full_name",
			label: "Full Name",
			type: "text",
			render: () => renderFunctions.personName(person),
		},
		{
			name: "company_name",
			label: "Company",
			type: "text",
			render: () => {
				if (!person.company) {
					return <span className="text-muted">No company assigned</span>;
				}
				// Use the original companyBadge render function
				return renderFunctions.companyBadge(person);
			},
		},
		{
			name: "email",
			label: "Email",
			type: "email",
			render: () => renderFunctions.email(person) || <span className="text-muted">No email provided</span>,
		},
		{
			name: "phone",
			label: "Phone",
			type: "text",
			render: () => renderFunctions.phone(person) || <span className="text-muted">No phone provided</span>,
		},
		{
			name: "linkedin_url",
			label: "LinkedIn Profile",
			type: "url",
			render: () =>
				renderFunctions.linkedinUrl(person) || <span className="text-muted">No LinkedIn profile</span>,
		},
	];

	// Transform person data for display - ONLY include fields that DON'T have render functions
	const displayData = {
		...person,
		// Don't include these as they have render functions:
		// full_name, company_name, email, phone, linkedin_url
	};

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
		/>
	);
};

export default PersonViewModal;
