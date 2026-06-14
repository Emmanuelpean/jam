import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";
import { useViewport } from "../../contexts/ViewportContext";
import { EnrichedJobData } from "../../services/schemas/DataTables";

const FavouritesTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const { isTablet, isSmallDesktop } = useViewport();

	let defaultColumns: TableColumn<EnrichedJobData>[] =
		columns.length > 0
			? (columns as TableColumn<EnrichedJobData>[])
			: [
					tableColumns.titleColumn<EnrichedJobData>(),
					tableColumns.companyBadgeColumn<EnrichedJobData>(),
					tableColumns.locationBadgeColumn<EnrichedJobData>(),
					tableColumns.personalRatingColumn<EnrichedJobData>(),
					tableColumns.applicationStatusColumn<EnrichedJobData>(),
				];

	if (isSmallDesktop) {
		defaultColumns = defaultColumns.filter((col: TableColumn<EnrichedJobData>): boolean => col.key !== "location");
	}
	if (isTablet) {
		defaultColumns = defaultColumns.filter((col: TableColumn<EnrichedJobData>): boolean => col.key !== "company");
	}

	return (
		<DataTable<EnrichedJobData>
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
