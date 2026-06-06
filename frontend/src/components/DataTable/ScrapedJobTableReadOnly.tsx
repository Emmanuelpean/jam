import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobModal } from "../DataModal/ScrapedJobModal";
import { ScrapedJobData } from "../../services/schemas/Services";

interface ScrapedJobsTableReadOnlyProps extends DataTableProps {
	viewOnly?: boolean;
}

const ScrapedJobsTableReadOnly: React.FC<ScrapedJobsTableReadOnlyProps> = ({
	data = [],
	columns = [],
	onSuccess,
	viewOnly = false,
}: ScrapedJobsTableReadOnlyProps): JSX.Element => {
	const defaultColumns: TableColumn<ScrapedJobData>[] =
		columns.length > 0
			? (columns as TableColumn<ScrapedJobData>[])
			: [
					tableColumns.titleColumn<ScrapedJobData>(),
					tableColumns.scrapedCompanyColumn<ScrapedJobData>(),
					tableColumns.locationBadgeColumn<ScrapedJobData>(),
					tableColumns.salaryRangeColumn<ScrapedJobData>(),
					tableColumns.isImportedColumn<ScrapedJobData>(),
					tableColumns.isActiveColumn<ScrapedJobData>({ label: "Deleted" }),
					tableColumns.urlGenericColumn<ScrapedJobData>(),
					tableColumns.createdAtColumn<ScrapedJobData>({ label: "Date Received" }),
				];

	return (
		<>
			<DataTable<ScrapedJobData>
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
