import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";
import { EnrichedJobData } from "../../services/schemas/DataTables";

const UpcomingDeadlinesTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	let defaultColumns: TableColumn<EnrichedJobData>[] =
		columns.length > 0
			? (columns as TableColumn<EnrichedJobData>[])
			: [
					tableColumns.titleColumn<EnrichedJobData>(),
					tableColumns.companyBadgeColumn<EnrichedJobData>(),
					tableColumns.locationBadgeColumn<EnrichedJobData>(),
					tableColumns.daysUntilDeadlineColumn<EnrichedJobData>(),
				];

	return (
		<DataTable<EnrichedJobData>
			entityType="job"
			columns={defaultColumns}
			data={data}
			initialSortConfig={{ key: "days_until_deadline", direction: "asc" }}
			Modal={JobModal}
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			modalProps={{ defaultActiveTab: "job" }}
		/>
	);
};

export default UpcomingDeadlinesTable;
