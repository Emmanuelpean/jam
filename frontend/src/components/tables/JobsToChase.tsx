import React from "react";
import { DataTableProps, DataTable } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../modals/JobModal";

const JobToChaseTable: React.FC<DataTableProps> = ({
	data = [],
	onDataChange,
	error = null,
	columns = [],
	menuItems = [],
}) => {
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
			mode="controlled"
			data={data}
			onDataChange={onDataChange}
			error={error}
			columns={defaultColumns}
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
