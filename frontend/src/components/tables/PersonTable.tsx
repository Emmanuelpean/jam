import React from "react";
import { GenericTableWithModals, TableProps, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { PersonModal } from "../modals/PersonModal";

const PersonTable: React.FC<TableProps> = ({ onChange, data = null, columns = [] }) => {
	const {
		data: persons,
		loading,
		error,
		addItem,
		sortConfig,
		setSortConfig,
		updateItem,
		removeItem,
	} = useProvidedTableData(data, { key: "name", direction: "asc" }); // TODO sorting not working

	if (!columns.length) {
		columns = [
			tableColumns.personName!(),
			tableColumns.role!(),
			tableColumns.email!(),
			tableColumns.phone!(),
			tableColumns.linkedinUrl!(),
		];
	}

	return (
		<GenericTableWithModals
			data={persons}
			columns={columns}
			loading={loading}
			error={error}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			Modal={PersonModal}
			endpoint="persons"
			nameKey="name"
			itemType="Person"
			addItem={addItem}
			showAdd={false}
			showSearch={true}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={() => {}}
			modalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default PersonTable;
