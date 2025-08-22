import React from "react";
import { GenericTableWithModals, useTableData } from "./GenericTable";
import { columns } from "../rendering/view/TableColumnRenders";
import { JobApplicationUpdateFormModal, JobApplicationUpdateViewModal } from "../modals/JobApplicationUpdateModal";

const JobApplicationUpdatesTable = ({ jobApplicationId, onChange, updates = null }) => {
	const {
		data: updatesData,
		loading,
		error,
		addItem,
		updateItem,
		deleteItem,
	} = useTableData(
		"jobapplicationupdates",
		[jobApplicationId, updates],
		{ job_application_id: jobApplicationId },
		{ key: "date", direction: "desc" },
		updates,
	);

	const handleAddSuccess = (newEntry) => {
		addItem(newEntry);
		if (onChange) {
			onChange();
		}
	};

	const handleUpdateSuccess = (updatedEntry) => {
		updateItem(updatedEntry);
		if (onChange) {
			onChange();
		}
	};

	const handleDeleteSuccess = (deletedId) => {
		deleteItem(deletedId);
		if (onChange) {
			onChange();
		}
	};

	const ViewColumns = [columns.date(), columns.updateType(), columns.note()];

	const FormModalWithProps = (props) => (
		<JobApplicationUpdateFormModal
			{...props}
			jobApplicationId={jobApplicationId}
			onSuccess={props.isEdit ? handleUpdateSuccess : handleAddSuccess}
		/>
	);

	const ViewModalWithProps = (props) => (
		<JobApplicationUpdateViewModal {...props} jobApplicationId={jobApplicationId} />
	);

	return (
		<GenericTableWithModals
			data={updatesData}
			columns={ViewColumns}
			sortConfig={{ key: "date", direction: "desc" }}
			loading={loading}
			error={error}
			FormModal={FormModalWithProps}
			ViewModal={ViewModalWithProps}
			endpoint="jobapplicationupdates"
			nameKey="date"
			itemType="Update"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={handleDeleteSuccess}
			ModalSize="xl"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default JobApplicationUpdatesTable;
