import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";
import { EnrichedJobData } from "../../services/schemas/DataTables";

const JobsTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn<EnrichedJobData>[] =
		columns.length > 0
			? (columns as TableColumn<EnrichedJobData>[])
			: [
					tableColumns.titleColumn<EnrichedJobData>(),
					tableColumns.companyBadgeColumn<EnrichedJobData>(),
					tableColumns.applicationStatusColumn<EnrichedJobData>(),
					tableColumns.createdAtColumn<EnrichedJobData>(),
				];

	return (
		<DataTable<EnrichedJobData>
			entityType="job"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			Modal={JobModal}
			modalSize="xl"
			showAllEntries={true}
			compact={true}
			showAdd={false}
			showSearch={true}
		/>
	);
};

export default JobsTable;
