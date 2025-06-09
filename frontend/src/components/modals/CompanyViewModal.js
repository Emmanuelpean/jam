import React from "react";
import GenericModal from "../GenericModal";
// import { renderFunctions } from "../Renders";

const CompanyViewModal = ({ show, onHide, company, onEdit, size }) => {
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
			// render: () => renderFunctions.websiteUrl(company, true),
		},
		{
			name: "description",
			label: "Description",
			type: "textarea",
			// render: () => renderFunctions.description(company, true),
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
			size={size}
		/>
	);
};

export default CompanyViewModal;
