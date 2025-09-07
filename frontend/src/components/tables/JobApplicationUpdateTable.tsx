import React from "react";
import { GenericTableWithModals, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { JobApplicationUpdateModal } from "../modals/JobApplicationUpdateModal";

interface JobApplicationUpdatesTableProps {
	jobApplicationId: string | number;
	onChange?: () => void;
	data?: any[] | null;
}

const JobApplicationUpdatesTable: React.FC<JobApplicationUpdatesTableProps> = ({
	jobApplicationId,
	onChange,
	data = null,
}) => {
	const {
		data: updatesData,
		loading,
		error,
		addItem,
		updateItem,
		removeItem,
	} = useProvidedTableData(data, { key: "date", direction: "desc" });

	const handleAddSuccess = (newEntry: any) => {
		addItem(newEntry);
		if (onChange) {
			onChange();
		}
	};

	const handleUpdateSuccess = (updatedEntry: any) => {
		updateItem(updatedEntry);
		if (onChange) {
			onChange();
		}
	};

	const handleDeleteSuccess = (deletedId: string | number) => {
		removeItem(deletedId);
		if (onChange) {
			onChange();
		}
	};

	const ViewColumns = [tableColumns.date!(), tableColumns.updateType!(), tableColumns.note!()];

	const ModalWithProps = (props: any) => (
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
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			setData={() => {}}
		/>
	);
};

export default JobApplicationUpdatesTable;
