import React from "react";
import { DataTableProps, DataTable } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../modals/JobModal";
import { JobData } from "../../services/Schemas";

const JobToChaseTable: React.FC<DataTableProps> = ({ data = [], columns = [], menuItems = [] }) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [
					tableColumns.title(),
					tableColumns.companyBadge(),
					tableColumns.location(),
					tableColumns.daysSinceLastUpdate(),
					tableColumns.lastUpdateType(),
				];

	return (
		<DataTable
			entityType="jobs"
			columns={defaultColumns}
			data={data}
			initialSortConfig={{ key: "days_since_last_update", direction: "desc" }}
			Modal={JobModal}
			endpoint="jobs"
			nameKey="title"
			itemType="Job"
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			menuItems={menuItems}
			modalProps={{ defaultActiveTab: "application" }}
		/>
	);
};

export default JobToChaseTable;
