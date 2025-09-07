import React from "react";
import { GenericTableWithModals, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { JobAndApplicationModal } from "../modals/JobAndApplicationModal";

interface JobsTableProps {
	onChange?: () => void;
	data?: any[] | null;
	excludeColumns?: string | string[];
}

const JobsTable: React.FC<JobsTableProps> = ({ onChange, data = null, excludeColumns = [] }) => {
	const {
		data: jobs,
		loading,
		error,
		addItem,
		sortConfig,
		setSortConfig,
		updateItem,
		removeItem,
	} = useProvidedTableData(data, { key: "created_at", direction: "desc" });

	const columns = [
		tableColumns.title!(),
		tableColumns.company!(),
		tableColumns.location!(),
		tableColumns.createdAt!(),
	];
	if (!Array.isArray(excludeColumns)) {
		excludeColumns = [excludeColumns];
	}
	const filteredColumns = columns.filter((column) => !excludeColumns?.includes(column.key));

	return (
		<GenericTableWithModals
			data={jobs}
			columns={filteredColumns}
			loading={loading}
			error={error}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			Modal={JobAndApplicationModal}
			endpoint="jobs"
			nameKey="title"
			itemType="Job"
			addItem={addItem}
			showAdd={false}
			showSearch={true}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={() => {}}
			modalSize="xl"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default JobsTable;
