import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../../rendering/ViewRenders";

const JobViewModal = ({ show, onHide, job, onEdit, size }) => {
	if (!job) return null;
	console.log(job);
	const fields = [
		[viewFields.title(), viewFields.company()],
		[viewFields.location(), viewFields.jobApplication()],
		viewFields.description(),
		[viewFields.salaryRange(), viewFields.personalRating()],
		viewFields.url({"label": "Job URL"}),
		[viewFields.keywords(), viewFields.persons()],
	];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Job"
			size={size}
			fields={fields}
			data={job}
			onEdit={onEdit}
		/>
	);
};

export default JobViewModal;
