import React from "react";
import { DataTableProps, GenericTable } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../modals/JobModal";

const UpcomingDeadlinesTable: React.FC<DataTableProps> = ({ data = [], onDataChange, error = null, columns = [] }) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [tableColumns.title(), tableColumns.company(), tableColumns.location(), tableColumns.daysUntilDeadline()];

	return (
		<GenericTable
			mode="controlled"
			data={data}
			onDataChange={onDataChange}
			error={error}
			columns={defaultColumns}
			initialSortConfig={{ key: "days_until_deadline", direction: "asc" }}
			Modal={JobModal}
			endpoint="jobs"
			nameKey="title"
			itemType="Job"
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			modalProps={{ defaultActiveTab: "job" }}
		/>
	);
};

export default UpcomingDeadlinesTable;
