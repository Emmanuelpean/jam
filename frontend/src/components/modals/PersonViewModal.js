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
			render: () => renderFunctions.personName(person, true),
		},
		{
			name: "company_name",
			label: "Company",
			type: "text",
			render: () => renderFunctions.companyBadge(person, true),
		},
		{
			name: "email",
			label: "Email",
			type: "email",
			render: () => renderFunctions.email(person, true),
		},
		{
			name: "phone",
			label: "Phone",
			type: "text",
			render: () => renderFunctions.phone(person, true),
		},
		{
			name: "linkedin_url",
			label: "LinkedIn Profile",
			type: "url",
			render: () => renderFunctions.linkedinUrl(person, true),
		},
	];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Person Details"
			size={size}
			data={person}
			viewFields={viewFields}
			onEdit={onEdit}
			showEditButton={true}
			showSystemFields={true}
		/>
	);
};

export default PersonViewModal;
