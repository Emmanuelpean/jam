import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";

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
					tableColumns.isImportedColumn(),
					tableColumns.urlGenericColumn(),
					tableColumns.platformColumn(),
					tableColumns.createdAtColumn({ label: "Date Received" }),
				];

	return (
		<>
			<DataTable
				entityType="scrapedJob"
				mode="import"
				columns={defaultColumns}
				initialSortConfig={{ key: "created_at", direction: "desc" }}
				Modal={ScrapedJobModal}
				data={data}
				modalSize="xl"
				compact={true}
				showAdd={false}
				showSearch={false}
				menuItems={["import"]}
			/>
		</>
	);
};

export default ScrapedJobsTableReadOnly;
