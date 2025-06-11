import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../ViewRenders";

const CompanyViewModal = ({ show, onHide, company, onEdit, onDelete, size }) => {
	if (!company) return null;

	const fields = [viewFields.name, viewFields.url, viewFields.description];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Company"
			size={size}
			data={company}
			viewFields={fields}
			onEdit={onEdit}
			onDelete={onDelete}
		/>
	);
};

export default CompanyViewModal;
