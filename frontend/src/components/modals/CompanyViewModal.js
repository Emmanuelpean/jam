import React from "react";
import GenericModal from "../GenericModal";

const CompanyViewModal = ({ show, onHide, company, onEdit }) => {
	// Define view fields for company
	const viewFields = [
		{
			name: "name",
			label: "Company Name",
			type: "text",
		},
		{
			name: "url",
			label: "Website",
			type: "url",
		},
		{
			name: "description",
			label: "Description",
			type: "textarea",
		},
	];

	if (!company) return null;

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Company"
			data={company}
			viewFields={viewFields}
			onEdit={onEdit}
			showEditButton={true}
			showSystemFields={true}
			size="lg"
		/>
	);
};

export default CompanyViewModal;
