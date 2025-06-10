import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../ViewRenders";

const JobViewModal = ({ show, onHide, job, onEdit, size }) => {
	if (!job) return null;
	console.log(job);
	const fields = [
		viewFields.title,
		viewFields.company,
		viewFields.location,
		viewFields.status,
		viewFields.description,
		viewFields.salaryRange,
		viewFields.personalRating,
		viewFields.url,
	];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Job Application"
			size={size}
			viewFields={fields}
			data={job}
			onEdit={onEdit}
		/>
	);
};

export default JobViewModal;
