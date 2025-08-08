import React from "react";
import { GenericTableWithModals, useTableData } from "./TableSystem";
import { columns } from "../rendering/ColumnRenders";
import { InterviewFormModal, InterviewViewModal } from "../modals/InterviewModal";

const InterviewsTable = ({ jobApplicationId, onInterviewChange }) => {
	const {
		data: interviews,
		loading,
		error,
		addItem,
		updateItem,
		deleteItem,
	} = useTableData("interviews", [jobApplicationId], { job_application_id: jobApplicationId });

	const handleAddSuccess = (newInterview) => {
		addItem(newInterview);
		if (onInterviewChange) {
			onInterviewChange();
		}
	};

	const handleUpdateSuccess = (updatedInterview) => {
		updateItem(updatedInterview);
		if (onInterviewChange) {
			onInterviewChange();
		}
	};

	const handleDeleteSuccess = (deletedId) => {
		deleteItem(deletedId);
		if (onInterviewChange) {
			onInterviewChange();
		}
	};

	const interviewColumns = [columns.date(), columns.type(), columns.location(), columns.note()];

	const FormModalWithProps = (props) => (
		<InterviewFormModal
			{...props}
			interview={props.item}
			jobApplicationId={jobApplicationId}
			onSuccess={props.isEdit ? handleUpdateSuccess : handleAddSuccess}
		/>
	);

	const ViewModalWithProps = (props) => (
		<InterviewViewModal {...props} interview={props.item} jobApplicationId={jobApplicationId} />
	);

	return (
		<GenericTableWithModals
			data={interviews}
			columns={interviewColumns}
			sortConfig={{ key: "date", direction: "desc" }}
			loading={loading}
			error={error}
			FormModal={FormModalWithProps}
			ViewModal={ViewModalWithProps}
			endpoint="interviews"
			nameKey="date"
			itemType="Interview"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={handleDeleteSuccess}
			ModalSize="xl"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default InterviewsTable;
