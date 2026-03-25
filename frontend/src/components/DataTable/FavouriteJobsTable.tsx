import React, { JSX, useEffect, useState } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../DataModal/JobModal";

const FavouriteJobsTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
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
					tableColumns.applicationStatusColumn(),
				];

	if (windowWidth < 1300) {
		defaultColumns = defaultColumns.filter((col: TableColumn): boolean => col.key !== "locationBadge");
	}
	if (windowWidth < 1000) {
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
