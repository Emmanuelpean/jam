import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { ScrapedJobFilterModal } from "../modals/ScrapedJobFilterModal";

const ScrapedJobFilterTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.typeColumn(),
					tableColumns.operatorColumn(),
					tableColumns.valueColumn({ type: "text" }),
					tableColumns.isActiveColumn(),
					tableColumns.caseSensitiveColumn(),
				];

	return (
		<DataTable
			entityType="scrapedJobFilters"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "name", direction: "asc" }}
			Modal={ScrapedJobFilterModal}
			nameKey="name"
			itemType="Scraped Job Filter"
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			showSearch={true}
		/>
	);
};

export default ScrapedJobFilterTable;
