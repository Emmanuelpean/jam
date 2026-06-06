import React, { JSX } from "react";
import { DataTable, DataTableProps } from "./DataTable";
import { TableColumn, tableColumns } from "../rendering/view/TableColumns";
import { PersonModal } from "../DataModal/PersonModal";
import { PersonData } from "../../services/schemas/DataTables";

const PersonTable: React.FC<DataTableProps> = ({ data = [], columns = [] }: DataTableProps): JSX.Element => {
	const defaultColumns: TableColumn<PersonData>[] =
		columns.length > 0
			? (columns as TableColumn<PersonData>[])
			: [
					tableColumns.personNameColumn<PersonData>(),
					tableColumns.roleColumn<PersonData>(),
					tableColumns.emailColumn<PersonData>(),
					tableColumns.phoneColumn<PersonData>(),
					tableColumns.linkedinUrlColumn<PersonData>(),
				];

	return (
		<DataTable<PersonData>
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
