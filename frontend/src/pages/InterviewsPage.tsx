import React from "react";
import DataTable from "../components/tables/DataTable";
import { InterviewModal } from "../components/DataModal/InterviewModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const InterviewsPage = () => {
	const columns = [
		tableColumns.jobBadgeColumn(),
		tableColumns.interviewerBadgesColumn(),
		tableColumns.dateColumn(),
		tableColumns.typeColumn(),
		tableColumns.locationBadgeColumn(),
		tableColumns.createdAtColumn(),
	];

	return (
		<DataTable
			entityType="interview"
			initialSortConfig={{ key: "date", direction: "desc" }}
			title="Interviews"
			columns={columns}
			Modal={InterviewModal}
		/>
	);
};

export default InterviewsPage;
