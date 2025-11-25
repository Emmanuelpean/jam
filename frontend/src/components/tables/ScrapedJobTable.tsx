import React, { JSX } from "react";
import { DataTableProps, DataTable } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../modals/ScrapedJobModal";

const ScrapedJobsTable: React.FC<DataTableProps> = ({ columns = [] }: DataTableProps): JSX.Element => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.scrapedCompanyColumn(),
					tableColumns.scrapedLocationColumn(),
					tableColumns.salaryRangeColumn(),
					tableColumns.descriptionColumn(),
					tableColumns.urlGenericColumn(),
					tableColumns.platformColumn(),
					tableColumns.createdAtColumn({ label: "Date Received" }),
				];

	return (
		<DataTable
			entityType="scrapedJobs"
			mode="import"
			columns={defaultColumns}
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			Modal={ScrapedJobModal}
			endpoint="scraped_jobs"
			nameKey="title"
			itemType="Scraped Job"
			modalSize="xl"
			showAdd={false}
			showSearch={true}
		/>
	);
};

export default ScrapedJobsTable;
