import React from "react";
import { GenericTableWithModals, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { InterviewModal } from "../modals/InterviewModal";
import { DataModalProps } from "../modals/AggregatorModal";

interface InterviewsTableProps {
	jobApplicationId?: number;
	onChange?: () => void;
	data?: any[] | null;
}

const InterviewsTable: React.FC<InterviewsTableProps> = ({ jobApplicationId, onChange, data = null }) => {
	const {
		data: interviewData,
		loading,
		error,
		addItem,
		sortConfig,
		setSortConfig,
		updateItem,
		removeItem,
	} = useProvidedTableData(data, { key: "date", direction: "desc" });

	const ViewColumns = [tableColumns.date!(), tableColumns.type!(), tableColumns.location!(), tableColumns.note!()];

	const ModalWithProps: React.FC<DataModalProps> = (props) => (
		<InterviewModal {...props} jobApplicationId={jobApplicationId} />
	);

	return (
		<GenericTableWithModals
			data={interviewData}
			columns={ViewColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			loading={loading}
			error={error}
			Modal={ModalWithProps}
			endpoint="interviews"
			nameKey="date"
			itemType="Interview"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={() => {}}
			modalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default InterviewsTable;
