import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../ViewRenders";

const CompanyViewModal = ({ show, onHide, company, onEdit, size }) => {
	if (!company) return null; // TODO to remove if can prevent initial calling

	const fields = [viewFields.name, viewFields.url, viewFields.description];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Company"
			data={company}
			viewFields={fields}
			onEdit={onEdit}
			size={size}
		/>
	);
};

export default CompanyViewModal;
