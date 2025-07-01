import React from "react";
import { GenericTableWithModals, useTableData } from "./TableSystem";
import { columns } from "../rendering/ColumnRenders";
import { InterviewFormModal, InterviewViewModal } from "../modals/interview/InterviewModal";
import "./InterviewTable.css";

const InterviewsTable = ({ jobApplicationId, onInterviewChange }) => {
	const {
		data: interviews,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		deleteItem,
	} = useTableData("interviews", [jobApplicationId], { jobapplication_id: jobApplicationId });

	// Wrapper for success handlers to trigger parent refresh
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

	// Define columns for interview table
	const interviewColumns = [columns.date(), columns.type(), columns.location(), columns.note()];

	// Create wrapper components that pass the jobApplicationId and handle the new modal structure
	const InterviewFormModalWithProps = (props) => (
		<InterviewFormModal
			{...props}
			interview={props.item}
			jobApplicationId={jobApplicationId}
			onSuccess={props.isEdit ? handleUpdateSuccess : handleAddSuccess}
		/>
	);

	const InterviewViewModalWithProps = (props) => (
		<InterviewViewModal {...props} interview={props.item} jobApplicationId={jobApplicationId} />
	);

	return (
		<div className="interviews-table-container">
			<div className="mb-3">
				<h6 className="mb-3">Interviews {interviews.length > 0 && `(${interviews.length})`}</h6>

				<GenericTableWithModals
					data={interviews}
					columns={interviewColumns}
					sortConfig={sortConfig}
					onSort={setSortConfig}
					searchTerm={searchTerm}
					onSearchChange={setSearchTerm}
					loading={loading}
					error={error}
					FormModal={InterviewFormModalWithProps}
					ViewModal={InterviewViewModalWithProps}
					endpoint="interviews"
					nameKey="date"
					itemType="Interview"
					addItem={addItem}
					updateItem={updateItem}
					removeItem={handleDeleteSuccess}
					formModalSize="xl"
					viewModalSize="xl"
					isInModal={true}
					showAllEntries={true}
				/>
			</div>
		</div>
	);
};

export default InterviewsTable;
