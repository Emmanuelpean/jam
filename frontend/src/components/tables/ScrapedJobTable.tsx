import React from "react";
import { DataTableProps, DataTable } from "./DataTable";
import { tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../modals/ScrapedJobModal";

const ScrapedJobsTable: React.FC<DataTableProps> = ({ onDataChange, columns = [] }) => {
	const defaultColumns =
		columns.length > 0
			? columns
			: [
					tableColumns.title(),
					tableColumns.scrapedCompany(),
					tableColumns.scrapedLocation(),
					tableColumns.salaryRange(),
					tableColumns.description(),
					tableColumns.url(),
					tableColumns.createdAt({ label: "Date Received" }),
				];

	return (
		<DataTable
			mode="import"
			onDataChange={onDataChange}
			columns={defaultColumns}
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			Modal={ScrapedJobModal}
			endpoint="scraped_jobs"
			nameKey="title"
			itemType="Scraped Job"
			modalSize="xl"
			showAllEntries={true}
			showAdd={false}
			showSearch={false}
		/>
	);
};

export default ScrapedJobsTable;
