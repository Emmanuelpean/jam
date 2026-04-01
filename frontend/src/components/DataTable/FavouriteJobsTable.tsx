import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";
import { useViewport } from "../../contexts/ViewportContext";

const FavouriteJobsTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const { isTablet, isSmallDesktop } = useViewport();

	let defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.companyBadgeColumn(),
					tableColumns.locationBadgeColumn(),
					tableColumns.applicationStatusColumn(),
				];

	if (isSmallDesktop) {
		defaultColumns = defaultColumns.filter((col: TableColumn): boolean => col.key !== "locationBadge");
	}
	if (isTablet) {
		defaultColumns = defaultColumns.filter((col: TableColumn): boolean => col.key !== "companyBadge");
	}

	return (
		<DataTable
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
