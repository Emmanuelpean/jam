import React from "react";
import GenericModal from "../GenericModal";
import { viewFields } from "../../rendering/ViewRenders";

const JobApplicationViewModal = ({ job, jobApplication, show, onHide, onEdit, size }) => {
	// Accept both prop names for flexibility
	const data = job || jobApplication;

	if (!data) return null;

	const fields = [
		viewFields.date(),
		viewFields.status(),
		viewFields.job(),
		viewFields.appliedVia(),
		viewFields.aggregator(),
		viewFields.url({label: "Application URL"}),
		viewFields.note(),
		viewFields.files()
	];

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Job Application"
			size={size}
			viewFields={fields}
			data={data}
			onEdit={onEdit}
		/>
	);
};

export default JobApplicationViewModal;
