import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";

interface ScrapedJobsTableReadOnlyProps extends DataTableProps {
	viewOnly?: boolean;
}

const ScrapedJobsTableReadOnly: React.FC<ScrapedJobsTableReadOnlyProps> = ({
	data = [],
	columns = [],
	onSuccess,
	viewOnly = false,
}: ScrapedJobsTableReadOnlyProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.scrapedCompanyColumn(),
					tableColumns.locationBadgeColumn(),
					tableColumns.salaryRangeColumn(),
					tableColumns.isImportedColumn(),
					tableColumns.isActiveColumn({ label: "Deleted" }),
					tableColumns.urlGenericColumn(),
					tableColumns.createdAtColumn({ label: "Date Received" }),
				];

	return (
		<>
			<DataTable
				entityType="scrapedJob"
				mode={viewOnly ? "default" : "import"}
				columns={defaultColumns}
				initialSortConfig={{ key: "title", direction: "asc" }}
				Modal={ScrapedJobModal}
				data={data}
				modalSize="xl"
				compact={true}
				showAdd={false}
				showSearch={false}
				menuItems={viewOnly ? ["view"] : (item: any): string[] => (item.is_imported ? ["view"] : ["import"])}
				modalProps={{ canEdit: false }}
				rowMode={
					viewOnly
						? undefined
						: (item: any): "default" | "import" =>
								item.is_imported || !item.is_active ? "default" : "import"
				}
				onSuccess={onSuccess}
			/>
		</>
	);
};

export default ScrapedJobsTableReadOnly;
