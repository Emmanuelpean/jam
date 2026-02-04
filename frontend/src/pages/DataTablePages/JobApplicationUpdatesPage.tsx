import React from "react";
import { JobApplicationUpdateModal } from "../../components/DataModal/JobApplicationUpdateModal";
import { DataTable } from "../../components/DataTable/DataTable";
import { tableColumns } from "../../components/rendering/view/TableColumns";

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
			entityType="jobApplicationUpdate"
			initialSortConfig={{ key: "date", direction: "desc" }}
			title="Job Application Updates"
			columns={columns}
			Modal={JobApplicationUpdateModal}
			modalSize="lg"
		/>
	);
};

export default JobApplicationUpdatesPage;
