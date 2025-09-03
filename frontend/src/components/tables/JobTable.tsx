import React from "react";
import { GenericTableWithModals, useProvidedTableData } from "./GenericTable";
import { columns } from "../rendering/view/TableColumnRenders";
import { JobAndApplicationModal } from "../modals/JobAndApplicationModal";

interface JobsTableProps {
	onChange?: () => void;
	data?: any[] | null;
}

const JobsTable: React.FC<JobsTableProps> = ({ onChange, data = null }) => {
	const {
		data: jobs,
		loading,
		error,
		addItem,
		sortConfig,
		setSortConfig,
		updateItem,
		deleteItem,
	} = useProvidedTableData(data, { key: "created_at", direction: "desc" });

	const ViewColumns = [columns.title!(), columns.company!(), columns.location!(), columns.createdAt!()];

	return (
		<GenericTableWithModals
			data={jobs}
			columns={ViewColumns}
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
			removeItem={deleteItem}
			setData={() => {}}
			ModalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default JobsTable;
