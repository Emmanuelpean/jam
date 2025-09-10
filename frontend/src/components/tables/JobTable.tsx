import React from "react";
import { GenericTableWithModals, useProvidedTableData } from "./GenericTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumnRenders";
import { JobAndApplicationModal } from "../modals/JobAndApplicationModal";

interface JobsTableProps {
	onChange?: () => void;
	data?: any[] | null;
	columns?: TableColumn[];
}

const JobsTable: React.FC<JobsTableProps> = ({ onChange, data = null, columns = [] }) => {
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
		columns = [tableColumns.title!(), tableColumns.company!(), tableColumns.location!(), tableColumns.createdAt!()];
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
