import React from "react";
import { DataTable } from "../components/tables/DataTable";
import { JobModal } from "../components/modals/JobModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const JobsPage = () => {
	const columns = [
		tableColumns.titleColumn(),
		tableColumns.companyBadgeColumn(),
		tableColumns.locationBadgeColumn(),
		tableColumns.urlGenericColumn(),
		tableColumns.salaryRangeColumn(),
		tableColumns.personalRatingColumn(),
		tableColumns.applicationStatusColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<DataTable
			entityType="job"
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			title="Jobs"
			columns={columns}
			Modal={JobModal}
			nameKey="title"
			itemType="Job"
			modalSize="xl"
		/>
	);
};

export default JobsPage;
