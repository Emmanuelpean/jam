import React from "react";
import { DataTableProps, GenericTable } from "./GenericTable";
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
					tableColumns.createdAt(),
				];

	return (
		<GenericTable
			mode="import"
			onDataChange={onDataChange}
			columns={defaultColumns}
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			Modal={ScrapedJobModal}
			endpoint="scrapedjobs"
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
