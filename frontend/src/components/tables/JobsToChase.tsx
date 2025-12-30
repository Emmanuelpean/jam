import React, { JSX, useEffect, useState } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../modals/JobModal";

const JobToChaseTable: React.FC<DataTableProps> = ({
	data = [],
	columns = [],
	menuItems = [],
}: DataTableProps): JSX.Element => {
	const [windowWidth, setWindowWidth] = useState(window.innerWidth);

	let defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.titleColumn(),
					tableColumns.companyBadgeColumn(),
					tableColumns.locationBadgeColumn(),
					tableColumns.daysSinceLastUpdateColumn(),
					tableColumns.lastUpdateTypeColumn(),
				];

	useEffect(() => {
		const handleResize = (): void => setWindowWidth(window.innerWidth);
		window.addEventListener("resize", handleResize);
		return () => window.removeEventListener("resize", handleResize);
	}, []);

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
			initialSortConfig={{ key: "days_since_last_update", direction: "desc" }}
			Modal={JobModal}
			itemType="Job"
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			menuItems={menuItems}
			modalProps={{ defaultActiveTab: "application" }}
		/>
	);
};

export default JobToChaseTable;
