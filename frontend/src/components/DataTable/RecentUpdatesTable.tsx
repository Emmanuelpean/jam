import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";

const RecentUpdatesTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.companyBadgeColumn(),
					tableColumns.applicationStatusColumn(),
					tableColumns.lastUpdateTypeColumn(),
					tableColumns.daysSinceLastUpdateColumn(),
				];

	return (
		<DataTable
			entityType="job"
			columns={defaultColumns}
			data={data}
			initialSortConfig={{ key: "days_since_last_update", direction: "asc" }}
			Modal={JobModal}
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			menuItems={["view", "edit", "delete"]}
			modalProps={{ defaultActiveTab: "application" }}
		/>
	);
};

export default RecentUpdatesTable;
