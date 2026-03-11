import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";

const ScrapedJobsTableReadOnly: React.FC<DataTableProps> = ({
	data = [],
	columns = [],
	onSuccess,
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
					tableColumns.isActiveColumn(),
					tableColumns.urlGenericColumn(),
					tableColumns.createdAtColumn({ label: "Date Received" }),
				];

	return (
		<>
			<DataTable
				entityType="scrapedJob"
				mode="import"
				columns={defaultColumns}
				initialSortConfig={{ key: "title", direction: "asc" }}
				Modal={ScrapedJobModal}
				data={data}
				modalSize="xl"
				compact={true}
				showAdd={false}
				showSearch={false}
				menuItems={(item: any): string[] => (item.is_imported ? ["view"] : ["import"])}
				modalProps={{ canEdit: false }}
				rowMode={(item: any): "default" | "import" =>
					item.is_imported || !item.is_active ? "default" : "import"
				}
				onSuccess={onSuccess}
			/>
		</>
	);
};

export default ScrapedJobsTableReadOnly;
