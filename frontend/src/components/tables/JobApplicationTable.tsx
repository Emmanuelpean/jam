import React from "react";
import { GenericTableWithModals, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { JobAndApplicationModal } from "../modals/JobAndApplicationModal";

interface JobsTableProps {
	onChange?: () => void;
	data?: any[] | null;
	excludeColumns?: string | string[];
}

const JobApplicationsTable: React.FC<JobsTableProps> = ({ onChange, data = null, excludeColumns = [] }) => {
	const {
		data: job_applications,
		loading,
		error,
		addItem,
		sortConfig,
		setSortConfig,
		updateItem,
		removeItem,
	} = useProvidedTableData(data, { key: "created_at", direction: "desc" });

	console.log("AAAA", job_applications);
	const columns = [
		tableColumns.title!({ accessKey: "job" }),
		tableColumns.company!({ accessKey: "job" }),
		tableColumns.location!({ accessKey: "job" }),
		tableColumns.createdAt!(),
	];
	if (!Array.isArray(excludeColumns)) {
		excludeColumns = [excludeColumns];
	}
	const filteredColumns = columns.filter((column) => !excludeColumns?.includes(column.key));

	return (
		<GenericTableWithModals
			data={job_applications}
			columns={filteredColumns}
			loading={loading}
			error={error}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			Modal={JobAndApplicationModal}
			endpoint="jobapplications"
			nameKey="title"
			itemType="Job Application"
			addItem={addItem}
			showAdd={false}
			showSearch={true}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={() => {}}
			modalSize="xl"
			showAllEntries={true}
			compact={true}
			modalProps={{ defaultActiveTab: "job_application" }}
		/>
	);
};

export default JobApplicationsTable;
