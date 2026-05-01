import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";

const UpcomingDeadlinesTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	let defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.companyBadgeColumn(),
					tableColumns.locationBadgeColumn(),
					tableColumns.daysUntilDeadlineColumn(),
				];

	return (
		<DataTable
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
