import React from "react";
import { DataTableProps, DataTable } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../modals/JobModal";

const JobsTable: React.FC<DataTableProps> = ({ data = [], onDataChange, error = null, columns = [] }) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [
					tableColumns.title(),
					tableColumns.companyBadge(),
					tableColumns.applicationStatus(),
					tableColumns.createdAt(),
				];

	return (
		<DataTable
			mode="controlled"
			data={data}
			onDataChange={onDataChange}
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
