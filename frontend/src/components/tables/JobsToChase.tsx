import React from "react";
import { GenericTableWithModals, useProvidedTableData } from "./GenericTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumnRenders";
import { JobAndApplicationModal } from "../modals/JobAndApplicationModal";

interface DataTableProps {
	onChange?: () => void;
	data?: any[] | null;
}

const ApplicationToChaseTable: React.FC<DataTableProps> = ({ onChange, data = null }) => {
	const {
		data: jobApplicationData,
		loading,
		error,
		addItem,
		sortConfig,
		setSortConfig,
		updateItem,
		removeItem,
	} = useProvidedTableData(data, { key: "days_since_last_update", direction: "desc" });

	const columns: TableColumn[] = [
		tableColumns.title!(),
		tableColumns.company!(),
		tableColumns.location!(),
		tableColumns.daysSinceLastUpdate!({ accessKey: "job_application" }),
		tableColumns.lastUpdateType!({ accessKey: "job_application" }),
	];

	return (
		<GenericTableWithModals
			data={jobApplicationData}
			columns={columns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			loading={loading}
			error={error}
			Modal={JobAndApplicationModal}
			endpoint="jobapplications"
			nameKey="date"
			itemType="Job Application"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={() => {}}
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			modalProps={{ defaultActiveTab: "application" }}
		/>
	);
};

export default ApplicationToChaseTable;
