import React from "react";
import { JobApplicationUpdateModal } from "../components/modals/JobApplicationUpdateModal";
import { DataTable } from "../components/tables/DataTable";
import { tableColumns } from "../components/rendering/view/TableColumns";

const JobApplicationUpdatesPage = () => {
	const columns = [
		tableColumns.jobBadgeColumn(),
		tableColumns.dateColumn(),
		tableColumns.updateTypeColumn(),
		tableColumns.noteColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<DataTable
			entityType="jobApplicationUpdates"
			initialSortConfig={{ key: "date", direction: "desc" }}
			title="Job Application Updates"
			columns={columns}
			Modal={JobApplicationUpdateModal}
			nameKey="date"
			itemType="Job Application Update"
			modalSize="lg"
		/>
	);
};

export default JobApplicationUpdatesPage;
