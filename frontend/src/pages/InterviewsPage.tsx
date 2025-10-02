import React from "react";
import DataTable from "../components/tables/DataTable";
import { InterviewModal } from "../components/modals/InterviewModal";
import { tableColumns } from "../components/rendering/view/TableColumns";

const InterviewsPage = () => {
	const columns = [
		tableColumns.job(),
		tableColumns.interviewers(),
		tableColumns.date(),
		tableColumns.type(),
		tableColumns.location(),
		tableColumns.createdAt(),
	];

	return (
		<DataTable
			mode="api"
			endpoint="interviews"
			initialSortConfig={{ key: "date", direction: "desc" }}
			title="Interviews"
			columns={columns}
			Modal={InterviewModal}
			nameKey="date"
			itemType="Interview"
		/>
	);
};

export default InterviewsPage;
