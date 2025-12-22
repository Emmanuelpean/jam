import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../modals/ScrapedJobModal";

const ScrapedJobsTableReadOnly: React.FC<DataTableProps> = ({
	data = [],
	columns = [],
}: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.scrapedCompanyColumn(),
					tableColumns.scrapedLocationColumn(),
					tableColumns.salaryRangeColumn(),
					tableColumns.overallScore(),
					tableColumns.urlGenericColumn(),
					tableColumns.platformColumn(),
					tableColumns.createdAtColumn({ label: "Date Received" }),
				];

	return (
		<>
			<DataTable
				entityType="scrapedJobs"
				columns={defaultColumns}
				initialSortConfig={{ key: "created_at", direction: "desc" }}
				Modal={ScrapedJobModal}
				nameKey="title"
				data={data}
				itemType="Scraped Job"
				modalSize="xl"
				compact={true}
				showAdd={false}
				showSearch={false}
				menuItems={["view"]}
				modalProps={{ canEdit: false }}
			/>
		</>
	);
};

export default ScrapedJobsTableReadOnly;
