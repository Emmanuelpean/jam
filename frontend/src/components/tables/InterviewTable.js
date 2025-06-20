import React, { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import GenericTable, { createGenericDeleteHandler, createTableActions } from "./GenericTable";
import { columns } from "../rendering/ColumnRenders";
import InterviewFormModal from "../modals/InterviewFormModal";
import InterviewViewModal from "../modals/InterviewViewModal";
import AlertModal from "../AlertModal";
import useGenericAlert from "../../hooks/useGenericAlert";
import "./InterviewTable.css";

const InterviewsTable = ({ interviews = [], jobApplicationId, onInterviewChange }) => {
	const { token } = useAuth();
	const [showModal, setShowModal] = useState(false);
	const [showViewModal, setShowViewModal] = useState(false);
	const [showEditModal, setShowEditModal] = useState(false);
	const [selectedInterview, setSelectedInterview] = useState(null);

	const { alertState, showConfirm, showError, hideAlert } = useGenericAlert();

	// Handle view interview
	const handleView = (interview) => {
		setSelectedInterview(interview);
		setShowViewModal(true);
	};

	// Handle edit interview
	const handleEdit = (interview) => {
		setSelectedInterview(interview);
		setShowEditModal(true);
	};

	// Handle add success
	const handleAddSuccess = (newInterview) => {
		if (onInterviewChange) {
			onInterviewChange();
		}
		setShowModal(false);
	};

	// Handle edit success
	const handleEditSuccess = (updatedInterview) => {
		if (onInterviewChange) {
			onInterviewChange();
		}
		setShowEditModal(false);
		setSelectedInterview(null);
	};

	// Handle edit modal close
	const handleEditModalClose = () => {
		setShowEditModal(false);
		setSelectedInterview(null);
	};

	// Create reusable delete handler using the generic function
	const handleDelete = createGenericDeleteHandler({
		endpoint: "interviews",
		token,
		showConfirm,
		showError,
		removeItem: (id) => {
			if (onInterviewChange) {
				onInterviewChange();
			}
		},
		nameKey: "date",
		itemType: "Interview",
	});

	// Define columns for interview table
	const interviewColumns = [columns.date, columns.location, columns.note];

	// Define actions for each row
	const tableActions = createTableActions([
		{ type: "view", onClick: handleView },
		{ type: "edit", onClick: handleEdit },
		{ type: "delete", onClick: handleDelete },
	]);

	return (
		<div className="interviews-table-container">
			<div className="mb-3">
				<h6 className="mb-3">Interviews {interviews.length > 0 && `(${interviews.length})`}</h6>

				<GenericTable
					data={interviews}
					columns={interviewColumns}
					actions={tableActions}
					onAddClick={() => setShowModal(true)}
					addButtonText="Add Interview"
					emptyMessage="No interviews found"
				/>

				{/* Modals */}
				<InterviewFormModal
					show={showModal}
					size="xl"
					onHide={() => setShowModal(false)}
					onSuccess={handleAddSuccess}
					jobApplicationId={jobApplicationId}
				/>

				<InterviewFormModal
					show={showEditModal}
					onHide={handleEditModalClose}
					onSuccess={handleEditSuccess}
					initialData={selectedInterview || {}}
					isEdit={true}
					size="xl"
					jobApplicationId={jobApplicationId}
				/>

				<InterviewViewModal
					show={showViewModal}
					onHide={() => setShowViewModal(false)}
					interview={selectedInterview}
					onEdit={handleEdit}
					size="xl"
				/>

				{/* Alert Modal using GenericModal - handles both alerts and confirmations */}
				<AlertModal alertState={alertState} hideAlert={hideAlert} />
			</div>
		</div>
	);
};

export default InterviewsTable;