import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../../rendering/ViewRenders";

const InterviewViewModal = ({ show, onHide, interview, onEdit, onDelete, size }) => {
	if (!interview) return null;

	const fields = [
		viewFields.date,
		viewFields.type,
		viewFields.location,
		viewFields.interviewers,
		viewFields.note,
	];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Interview"
			size={size}
			data={interview}
			viewFields={fields}
			onEdit={onEdit}
			onDelete={onDelete}
		/>
	);
};

export default InterviewViewModal;
