import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { InterviewModal } from "../modals/InterviewModal";

interface InterviewsTableProps extends DataTableProps {
	jobId?: number;
}

const InterviewsTable: React.FC<InterviewsTableProps> = ({
	jobId,
	data = [],
	columns = [],
}: InterviewsTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.dateColumn(),
					tableColumns.typeColumn(),
					tableColumns.locationBadgeColumn(),
					tableColumns.noteColumn(),
				];

	return (
		<DataTable
			entityType="interviews"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "date", direction: "desc" }}
			Modal={InterviewModal}
			modalProps={{ jobId }}
			nameKey="date"
			itemType="Interview"
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			showAdd={true}
		/>
	);
};

export default InterviewsTable;
