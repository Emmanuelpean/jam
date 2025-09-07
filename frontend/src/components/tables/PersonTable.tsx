import React from "react";
import { GenericTableWithModals, useProvidedTableData } from "./GenericTable";
import { tableColumns } from "../rendering/view/TableColumnRenders";
import { PersonModal } from "../modals/PersonModal";

interface PersonTableProps {
	onChange?: () => void;
	data?: any[] | null;
}

const PersonTable: React.FC<PersonTableProps> = ({ onChange, data = null }) => {
	const {
		data: persons,
		loading,
		error,
		addItem,
		sortConfig,
		setSortConfig,
		updateItem,
		deleteItem,
	} = useProvidedTableData(data, { key: "name", direction: "asc" }); // TODO sorting not working

	const ViewColumns = [
		tableColumns.personName!(),
		tableColumns.role!(),
		tableColumns.email!(),
		tableColumns.phone!(),
		tableColumns.linkedinUrl!(),
	];

	return (
		<GenericTableWithModals
			data={persons}
			columns={ViewColumns}
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
			removeItem={deleteItem}
			setData={() => {}}
			ModalSize="lg"
			showAllEntries={true}
			compact={true}
		/>
	);
};

export default PersonTable;
