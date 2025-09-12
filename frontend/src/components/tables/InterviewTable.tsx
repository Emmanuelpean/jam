import React from "react";
import { GenericTableWithModals, TableProps, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { InterviewModal } from "../modals/InterviewModal";
import { DataModalProps } from "../modals/AggregatorModal";

interface InterviewsTableProps extends TableProps {
	jobId?: number;
	showAdd?: boolean;
}

const InterviewsTable: React.FC<InterviewsTableProps> = ({
	jobId,
	onChange,
	data = null,
	columns = [],
	showAdd = true,
}) => {
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

	if (!columns.length) {
		columns = [tableColumns.date!(), tableColumns.type!(), tableColumns.location!(), tableColumns.note!()];
	}

	const ModalWithProps: React.FC<DataModalProps> = (props) => <InterviewModal {...props} jobId={jobId} />;

	return (
		<GenericTableWithModals
			data={interviewData}
			columns={columns}
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
			showAdd={showAdd}
		/>
	);
};

export default InterviewsTable;
