import React from "react";
import { GenericTable, GenericTableWithModalsProps, TableProps } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../modals/JobModal";

const JobsTable: React.FC<TableProps> = ({ data = [], onDataChange, loading = false, error = null, columns = [] }) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [
					tableColumns.title(),
					tableColumns.company(),
					tableColumns.applicationStatus(),
					tableColumns.createdAt(),
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
			loading={loading}
			error={error}
			columns={defaultColumns}
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			Modal={JobModal}
			endpoint="jobs"
			nameKey="title"
			itemType="Job"
			modalSize="xl"
			showAllEntries={true}
			compact={true}
			showAdd={false}
			showSearch={true}
		/>
	);
};

export default JobsTable;
