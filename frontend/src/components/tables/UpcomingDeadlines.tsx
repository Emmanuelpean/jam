import React, { useEffect, useState } from "react";
import { DataTableProps, DataTable } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { JobModal } from "../modals/JobModal";

const UpcomingDeadlinesTable: React.FC<DataTableProps> = ({ data = [], columns = [] }) => {
	const [windowWidth, setWindowWidth] = useState(window.innerWidth);

	useEffect(() => {
		const handleResize = () => setWindowWidth(window.innerWidth);
		window.addEventListener("resize", handleResize);
		return () => window.removeEventListener("resize", handleResize);
	}, []);

	let defaultColumns =
		columns.length > 0
			? columns
			: [
					tableColumns.title(),
					tableColumns.companyBadge(),
					tableColumns.location(),
					tableColumns.daysUntilDeadline(),
				];

	if (windowWidth < 1300) {
		defaultColumns = defaultColumns.filter((col: TableColumn): boolean => col.key !== "location");
	}
	if (windowWidth < 1000) {
		defaultColumns = defaultColumns.filter((col: TableColumn): boolean => col.key !== "company");
	}

	return (
		<DataTable
			entityType="jobs"
			columns={defaultColumns}
			data={data}
			initialSortConfig={{ key: "days_until_deadline", direction: "asc" }}
			Modal={JobModal}
			nameKey="title"
			itemType="Job"
			modalSize="xl"
			showSearch={false}
			showAdd={false}
			modalProps={{ defaultActiveTab: "job" }}
		/>
	);
};

export default UpcomingDeadlinesTable;
