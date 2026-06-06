import React from "react";
import DataTable from "../../components/DataTable/DataTable";
import { InterviewModal } from "../../components/DataModal/InterviewModal";
import { tableColumns } from "../../components/rendering/view/TableColumns";
import { EnrichedInterviewData } from "../../services/schemas/DataTables";

const InterviewsPage = () => {
	const columns = [
		tableColumns.jobBadgeColumn<EnrichedInterviewData>(),
		tableColumns.interviewerBadgesColumn<EnrichedInterviewData>(),
		tableColumns.dateColumn<EnrichedInterviewData>(),
		tableColumns.interviewTypeColumn<EnrichedInterviewData>(),
		tableColumns.locationBadgeColumn<EnrichedInterviewData>(),
		tableColumns.createdAtColumn<EnrichedInterviewData>(),
	];

	return (
		<DataTable<EnrichedInterviewData>
			entityType="interview"
			initialSortConfig={{ key: "date", direction: "desc" }}
			title="Interviews"
			columns={columns}
			Modal={InterviewModal}
			enableColumnConfig={true}
		/>
	);
};

export default InterviewsPage;
