import React from "react";
import { DataTable } from "../components/tables/DataTable";
import { JobModal } from "../components/modals/JobModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const JobsPage = () => {
	const columns = [
		tableColumns.title(),
		tableColumns.companyBadge(),
		tableColumns.location(),
		tableColumns.urlGeneric(),
		tableColumns.salaryRange(),
		tableColumns.personalRating(),
		tableColumns.applicationStatus(),
		tableColumns.createdAt(),
	];

	return (
		<DataTable
			entityType="jobs"
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
