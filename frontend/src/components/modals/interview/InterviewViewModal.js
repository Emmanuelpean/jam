import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../../rendering/ViewRenders";

const InterviewViewModal = ({ show, onHide, company, onEdit, onDelete, size }) => {
	if (!company) return null;

	const fields = [viewFields.date, viewFields.location, viewFields.type, viewFields.note];

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

export default InterviewViewModal;
