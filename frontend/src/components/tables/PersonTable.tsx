import React, { JSX } from "react";
import { DataTableProps, DataTable } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { PersonModal } from "../modals/PersonModal";

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
			entityType="persons"
			data={data}
			columns={defaultColumns}
			initialSortConfig={{ key: "name", direction: "asc" }}
			Modal={PersonModal}
			nameKey="name"
			itemType="Person"
			modalSize="lg"
			showAllEntries={true}
			compact={true}
			showAdd={false}
			showSearch={true}
		/>
	);
};

export default PersonTable;
