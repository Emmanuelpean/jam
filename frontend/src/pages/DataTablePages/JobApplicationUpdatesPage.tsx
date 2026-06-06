import React from "react";
import { JobApplicationUpdateModal } from "../../components/DataModal/JobApplicationUpdateModal";
import { DataTable } from "../../components/DataTable/DataTable";
import { tableColumns } from "../../components/rendering/view/TableColumns";
import { EnrichedJobApplicationUpdateData } from "../../services/schemas/DataTables";

const JobApplicationUpdatesPage = () => {
	const columns = [
		tableColumns.jobBadgeColumn<EnrichedJobApplicationUpdateData>(),
		tableColumns.dateColumn<EnrichedJobApplicationUpdateData>(),
		tableColumns.updateTypeColumn<EnrichedJobApplicationUpdateData>(),
		tableColumns.noteColumn<EnrichedJobApplicationUpdateData>(),
		tableColumns.createdAtColumn<EnrichedJobApplicationUpdateData>(),
	];

	return (
		<DataTable<EnrichedJobApplicationUpdateData>
			entityType="jobApplicationUpdate"
			initialSortConfig={{ key: "date", direction: "desc" }}
			title="Job Application Updates"
			columns={columns}
			Modal={JobApplicationUpdateModal}
			modalSize="lg"
			enableColumnConfig={true}
		/>
	);
};

export default JobApplicationUpdatesPage;
