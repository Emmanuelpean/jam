import React from "react";
import GenericModal from "../GenericModal/GenericModal";
import { viewFields } from "../../rendering/view/ModalFieldRenders";
// import InterviewsTable from "../../tables/InterviewTable";

const JobApplicationViewModal = ({ job, jobApplication, show, onHide, onEdit, size }) => {
	// Accept both prop names for flexibility
	const data = job || jobApplication;

	if (!data) return null;

	const fields = [
		[viewFields.date(), viewFields.status()],
		[viewFields.job(), viewFields.appliedVia()],
		[viewFields.url({ label: "Application URL" })],
		viewFields.note(),
	];
	//
	// // Custom content to include the interviews table
	// const customContent = data?.id ? (
	// 	<div className="mt-4">
	// 		<InterviewsTable
	// 			jobApplicationId={data.id}
	// 			onInterviewChange={() => {
	// 				// Optional: could add refresh logic here if needed
	// 			}}
	// 		/>
	// 	</div>
	// ) : null;

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Job Application"
			size={size}
			fields={fields}
			data={data}
			onEdit={onEdit}
			// customContent={customContent}
		/>
	);
};

export default JobApplicationViewModal;
