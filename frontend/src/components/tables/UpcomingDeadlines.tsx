import React from "react";
import { GenericTableWithModals, TableProps, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { JobAndApplicationModal } from "../modals/JobAndApplicationModal";

const UpcomingDeadlinesTable: React.FC<TableProps> = ({ data = null, columns = [] }) => {
	const {
		data: jobData,
		loading,
		error,
		addItem,
		sortConfig,
		setSortConfig,
		updateItem,
		removeItem,
	} = useProvidedTableData(data, { key: "days_since_last_update", direction: "desc" });

	if (!columns.length) {
		columns = [
			tableColumns.title!(),
			tableColumns.company!(),
			tableColumns.location!(),
			tableColumns.daysUntilDeadline!(),
		];
	}

	return (
		<GenericTableWithModals
			data={jobData}
			columns={columns}
			loading={loading}
			error={error}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			Modal={JobAndApplicationModal}
			endpoint="jobs"
			nameKey="name"
			itemType="Job"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={() => {}}
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			modalProps={{ defaultActiveTab: "job" }}
		/>
	);
};

export default UpcomingDeadlinesTable;
