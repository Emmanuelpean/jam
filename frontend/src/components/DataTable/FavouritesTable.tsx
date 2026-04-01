import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";
import { useViewport } from "../../contexts/ViewportContext";

const FavouritesTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const { isTablet, isSmallDesktop } = useViewport();

	let defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.companyBadgeColumn(),
					tableColumns.locationBadgeColumn(),
					tableColumns.personalRatingColumn(),
					tableColumns.applicationStatusColumn(),
				];

	if (isSmallDesktop) {
		defaultColumns = defaultColumns.filter((col: TableColumn): boolean => col.key !== "location");
	}
	if (isTablet) {
		defaultColumns = defaultColumns.filter((col: TableColumn): boolean => col.key !== "company");
	}

	return (
		<DataTable
			entityType="job"
			columns={defaultColumns}
			data={data}
			initialSortConfig={{ key: "personal_rating", direction: "desc" }}
			Modal={JobModal}
			modalSize="xl"
			showSearch={false}
			showAdd={false}
		/>
	);
};

export default FavouritesTable;
