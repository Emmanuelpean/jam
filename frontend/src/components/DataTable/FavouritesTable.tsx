import React, { JSX, useEffect, useState } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";

const FavouritesTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const [windowWidth, setWindowWidth] = useState(window.innerWidth);

	useEffect(() => {
		const handleResize = (): void => setWindowWidth(window.innerWidth);
		window.addEventListener("resize", handleResize);
		return () => window.removeEventListener("resize", handleResize);
	}, []);

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

	if (windowWidth < 1300) {
		defaultColumns = defaultColumns.filter((col: TableColumn): boolean => col.key !== "location");
	}
	if (windowWidth < 1000) {
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
