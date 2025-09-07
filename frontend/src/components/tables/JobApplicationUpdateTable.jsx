import React from "react";
import { GenericTableWithModals, useTableData } from "./GenericTable.tsx";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { JobApplicationUpdateModal } from "../modals/JobApplicationUpdateModal";

const JobApplicationUpdatesTable = ({ jobApplicationId, onChange, data = null }) => {
	const {
		data: updatesData,
		loading,
		error,
		addItem,
		updateItem,
		deleteItem,
	} = useTableData(
		"jobapplicationupdates",
		[jobApplicationId, data],
		{ job_application_id: jobApplicationId },
		{ key: "date", direction: "desc" },
		data,
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

	const ViewColumns = [tableColumns.date(), tableColumns.updateType(), tableColumns.note()];

	const ModalWithProps = (props) => (
		<JobApplicationUpdateModal
			{...props}
			jobApplicationId={jobApplicationId}
			onSuccess={
				props.submode === "add"
					? handleAddSuccess
					: props.submode === "edit"
						? handleUpdateSuccess
						: props.onSuccess
			}
		/>
	);

	return (
		<GenericTableWithModals
			data={updatesData}
			columns={ViewColumns}
			sortConfig={{ key: "date", direction: "desc" }}
			loading={loading}
			error={error}
			Modal={ModalWithProps}
			endpoint="jobapplicationupdates"
			nameKey="date"
			itemType="Update"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={handleDeleteSuccess}
			ModalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default JobApplicationUpdatesTable;
