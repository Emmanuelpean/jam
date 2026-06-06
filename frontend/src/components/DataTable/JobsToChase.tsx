import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";
import { EnrichedJobData, JobData } from "../../services/schemas/DataTables";

const JobToChaseTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	let defaultColumns: TableColumn<EnrichedJobData>[] =
		columns.length > 0
			? (columns as TableColumn<EnrichedJobData>[])
			: [
					tableColumns.titleColumn<EnrichedJobData>(),
					tableColumns.companyBadgeColumn<EnrichedJobData>(),
					tableColumns.locationBadgeColumn<EnrichedJobData>(),
					tableColumns.daysSinceLastUpdateColumn<EnrichedJobData>(),
					tableColumns.lastUpdateTypeColumn<EnrichedJobData>(),
				];

	return (
		<DataTable<EnrichedJobData>
			entityType="job"
			columns={defaultColumns}
			data={data}
			initialSortConfig={{ key: "days_since_last_update", direction: "desc" }}
			Modal={JobModal}
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			menuItems={(job: JobData) => [
				"view",
				"edit",
				"delete",
				"snooze",
				...(job.has_application ? ["followup"] : []),
			]}
			modalProps={{ defaultActiveTab: "application" }}
		/>
	);
};

export default JobToChaseTable;
