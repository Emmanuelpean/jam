import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";
import { useViewport } from "../../contexts/ViewportContext";
import { EnrichedJobData } from "../../services/schemas/DataTables";

const FavouriteJobsTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const { isTablet, isSmallDesktop } = useViewport();

	let defaultColumns: TableColumn<EnrichedJobData>[] =
		columns.length > 0
			? (columns as TableColumn<EnrichedJobData>[])
			: [
					tableColumns.titleColumn<EnrichedJobData>(),
					tableColumns.companyBadgeColumn<EnrichedJobData>(),
					tableColumns.locationBadgeColumn<EnrichedJobData>(),
					tableColumns.applicationStatusColumn<EnrichedJobData>(),
				];

	if (isSmallDesktop) {
		defaultColumns = defaultColumns.filter((col: TableColumn<EnrichedJobData>): boolean => col.key !== "locationBadge");
	}
	if (isTablet) {
		defaultColumns = defaultColumns.filter((col: TableColumn<EnrichedJobData>): boolean => col.key !== "companyBadge");
	}

	return (
		<DataTable<EnrichedJobData>
			entityType="job"
			columns={defaultColumns}
			data={data}
			initialSortConfig={{ key: "title", direction: "asc" }}
			Modal={JobModal}
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			modalProps={{ defaultActiveTab: "job" }}
		/>
	);
};

export default FavouriteJobsTable;
