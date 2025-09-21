import React from "react";
import GenericTable from "../components/tables/GenericTable";
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
		<GenericTable
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
