import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { InterviewModal } from "../DataModal/InterviewModal";

interface InterviewsTableProps extends DataTableProps {
	jobId?: number;
}

const InterviewsTable: React.FC<InterviewsTableProps> = ({
	jobId,
	data = [],
	columns = [],
	showAdd = true,
}: InterviewsTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.dateColumn(),
					tableColumns.interviewTypeColumn(),
					tableColumns.locationBadgeColumn(),
					tableColumns.noteColumn(),
				];

	return (
		<DataTable
			entityType="interview"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "date", direction: "desc" }}
			Modal={InterviewModal}
			modalProps={{ jobId }}
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			showAdd={showAdd}
		/>
	);
};

export default InterviewsTable;
