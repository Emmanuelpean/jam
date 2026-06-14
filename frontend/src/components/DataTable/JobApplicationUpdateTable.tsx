import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobApplicationUpdateModal } from "../DataModal/JobApplicationUpdateModal";
import { useTour } from "../../contexts/TourContext";
import { EnrichedJobApplicationUpdateData } from "../../services/schemas/DataTables";

interface JobApplicationUpdatesTableProps extends DataTableProps {
	jobId: number;
}

const JobApplicationUpdatesTable: React.FC<JobApplicationUpdatesTableProps> = ({
	jobId,
	data = [],
	columns = [],
}: JobApplicationUpdatesTableProps): JSX.Element => {
	const defaultColumns: TableColumn<EnrichedJobApplicationUpdateData>[] =
		columns.length > 0
			? (columns as TableColumn<EnrichedJobApplicationUpdateData>[])
			: [
					tableColumns.dateColumn<EnrichedJobApplicationUpdateData>(),
					tableColumns.updateTypeColumn<EnrichedJobApplicationUpdateData>(),
					tableColumns.noteColumn<EnrichedJobApplicationUpdateData>(),
				];

	const { allowedContextMenuActions } = useTour();

	return (
		<DataTable<EnrichedJobApplicationUpdateData>
			entityType="jobApplicationUpdate"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "date", direction: "desc" }}
			Modal={JobApplicationUpdateModal}
			modalProps={{ jobId }}
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			menuItems={(item) => {
				const all = ["view", "edit", "delete"];
				return allowedContextMenuActions ? all.filter((a) => allowedContextMenuActions.includes(a)) : all;
			}}
		/>
	);
};

export default JobApplicationUpdatesTable;
