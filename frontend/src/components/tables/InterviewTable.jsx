import React from "react";
import { GenericTableWithModals, useTableData } from "./GenericTable.tsx";
import { columns } from "../rendering/view/TableColumnRenders";
import { InterviewModal } from "../modals/InterviewModal";

const InterviewsTable = ({ jobApplicationId, onChange, data = null }) => {
	const {
		data: interviewData,
		loading,
		error,
		addItem,
		updateItem,
		deleteItem,
	} = useTableData(
		"interviews",
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

	const ViewColumns = [columns.date(), columns.type(), columns.location(), columns.note()];

	const ModalWithProps = (props) => (
		<InterviewModal
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
			data={interviewData}
			columns={ViewColumns}
			sortConfig={{ key: "date", direction: "desc" }}
			loading={loading}
			error={error}
			Modal={ModalWithProps}
			endpoint="interviews"
			nameKey="date"
			itemType="Interview"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={handleDeleteSuccess}
			ModalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default InterviewsTable;
