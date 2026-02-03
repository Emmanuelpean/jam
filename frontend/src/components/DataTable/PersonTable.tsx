import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { PersonModal } from "../DataModal/PersonModal";

const PersonTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn[] =
		columns.length > 0
			? columns
			: [
					tableColumns.personNameColumn(),
					tableColumns.roleColumn(),
					tableColumns.emailColumn(),
					tableColumns.phoneColumn(),
					tableColumns.linkedinUrlColumn(),
				];

	return (
		<DataTable
			entityType="person"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "name", direction: "asc" }}
			Modal={PersonModal}
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			showAdd={false}
			showSearch={true}
		/>
	);
};

export default PersonTable;
