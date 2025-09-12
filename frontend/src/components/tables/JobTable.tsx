import React from "react";
import { GenericTableWithModals, TableProps, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { JobAndApplicationModal } from "../modals/JobAndApplicationModal";

const JobsTable: React.FC<TableProps> = ({ onChange, data = null, columns = [] }) => {
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

	if (!columns.length) {
		columns = [
			tableColumns.title!(),
			tableColumns.company!(),
			tableColumns.applicationStatus!(),
			tableColumns.createdAt!(),
		];
	}

	return (
		<GenericTableWithModals
			data={jobs}
			columns={columns}
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
