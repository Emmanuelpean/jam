import React from "react";
import { GenericTable, GenericTableProps, DataTableProps } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../modals/JobModal";

const JobToChaseTable: React.FC<DataTableProps> = ({ data = [], onDataChange, error = null, columns = [] }) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [
					tableColumns.title(),
					tableColumns.company(),
					tableColumns.location(),
					tableColumns.daysSinceLastUpdate(),
					tableColumns.lastUpdateType(),
				];

	// Handle data changes and notify parent
	const handleDataChange = (newData: any[]) => {
		onDataChange?.(newData);
	};

	return (
		<GenericTable
			mode="controlled"
			data={data}
			onDataChange={handleDataChange}
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
			modalProps={{ defaultActiveTab: "application" }}
		/>
	);
};

export default JobToChaseTable;
