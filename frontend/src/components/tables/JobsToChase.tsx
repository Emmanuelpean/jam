import React from "react";
import { GenericTableWithModals, TableProps, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { JobAndApplicationModal } from "../modals/JobAndApplicationModal";

const ApplicationToChaseTable: React.FC<TableProps> = ({ onChange, data = null }) => {
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

	const columns = [
		tableColumns.title!(),
		tableColumns.company!(),
		tableColumns.location!(),
		tableColumns.daysSinceLastUpdate!(),
		tableColumns.lastUpdateType!(),
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
