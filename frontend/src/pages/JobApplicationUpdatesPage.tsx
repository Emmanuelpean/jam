import React from "react";
import { JobApplicationUpdateModal } from "../components/modals/JobApplicationUpdateModal";
import { DataTable } from "../components/tables/DataTable";
import { tableColumns } from "../components/rendering/view/TableColumns";

const JobApplicationUpdatesPage = () => {
	const columns = [
		tableColumns.job(),
		tableColumns.date(),
		tableColumns.updateType(),
		tableColumns.note(),
		tableColumns.createdAt(),
	];

	return (
		<DataTable
			mode="api"
			endpoint="jobapplicationupdates"
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
