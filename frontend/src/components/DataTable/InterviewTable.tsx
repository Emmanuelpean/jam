import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { InterviewModal } from "../DataModal/InterviewModal";
import { useTour } from "../../contexts/TourContext";
import { EnrichedInterviewData } from "../../services/schemas/DataTables";

interface InterviewsTableProps extends DataTableProps {
	jobId?: number;
}

const InterviewsTable: React.FC<InterviewsTableProps> = ({
	jobId,
	data = [],
	columns = [],
	showAdd = true,
}: InterviewsTableProps): JSX.Element => {
	const defaultColumns: TableColumn<EnrichedInterviewData>[] =
		columns.length > 0
			? (columns as TableColumn<EnrichedInterviewData>[])
			: [
					tableColumns.dateColumn<EnrichedInterviewData>(),
					tableColumns.interviewTypeColumn<EnrichedInterviewData>(),
					tableColumns.locationBadgeColumn<EnrichedInterviewData>(),
					tableColumns.noteColumn<EnrichedInterviewData>(),
				];

	const { allowedContextMenuActions } = useTour();

	return (
		<DataTable<EnrichedInterviewData>
			entityType="interview"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "date", direction: "desc" }}
			Modal={InterviewModal}
			modalProps={{ jobId }}
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			showAdd={showAdd}
			menuItems={(item) => {
				const all = ["view", "edit", "delete"];
				return allowedContextMenuActions ? all.filter((a) => allowedContextMenuActions.includes(a)) : all;
			}}
		/>
	);
};

export default InterviewsTable;
