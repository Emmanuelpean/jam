import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobApplicationUpdateModal } from "../DataModal/JobApplicationUpdateModal";

interface JobApplicationUpdatesTableProps extends DataTableProps {
	jobId: number;
}

const JobApplicationUpdatesTable: React.FC<JobApplicationUpdatesTableProps> = ({
	jobId,
	data = [],
	columns = [],
}: JobApplicationUpdatesTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [tableColumns.dateColumn(), tableColumns.updateTypeColumn(), tableColumns.noteColumn()];

	return (
		<DataTable
			entityType="jobApplicationUpdate"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "date", direction: "desc" }}
			Modal={JobApplicationUpdateModal}
			modalProps={{ jobId }}
			modalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default JobApplicationUpdatesTable;
