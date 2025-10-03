import React from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { InterviewModal, InterviewModalProps } from "../modals/InterviewModal";
import { DataModalProps } from "../modals/DataModal/DataModal";
import { InterviewData } from "../../services/Schemas";

interface InterviewsTableProps extends DataTableProps {
	jobId?: number;
}

const InterviewsTable: React.FC<InterviewsTableProps> = ({ jobId, data = [], columns = [], showAdd = true }) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [tableColumns.date(), tableColumns.type(), tableColumns.location(), tableColumns.note()];

	const ModalWithProps: React.FC<DataModalProps> = (props: InterviewModalProps) => (
		<InterviewModal {...props} jobId={jobId} />
	);

	return (
		<DataTable
			entityType="interviews"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "date", direction: "desc" }}
			Modal={ModalWithProps}
			endpoint="interviews"
			nameKey="date"
			itemType="Interview"
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			showAdd={showAdd}
		/>
	);
};

export default InterviewsTable;
