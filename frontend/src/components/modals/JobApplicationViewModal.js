import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../ViewRenders";

const JobApplicationViewModal = ({ jobApplication, show, onHide, onEdit, size }) => {
	if (!jobApplication) return null;

	const fields = [
		viewFields.title,
		viewFields.company,
		viewFields.location,
		viewFields.jobApplication,
		viewFields.description,
		viewFields.salaryRange,
		viewFields.personalRating,
		viewFields.url,
		viewFields.keywords,
		viewFields.persons,
	];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Job Application"
			size={size}
			viewFields={fields}
			data={jobApplication}
			onEdit={onEdit}
		/>
	);
};

export default JobApplicationViewModal;