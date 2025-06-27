import React from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/TableSystem";
import { PersonFormModal, PersonViewModal } from "../components/modals/person/PersonModal";
import { columns } from "../components/rendering/ColumnRenders";

const PersonsPage = () => {
	const {
		data: persons,
		setData: setPersons,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("persons");

	const tableColumns = [
		columns.personName(),
		columns.company(),
		columns.role(),
		columns.email(),
		columns.phone(),
		columns.linkedinUrl(),
		columns.createdAt(),
	];

	return (
		<GenericTableWithModals
			title="Persons"
			data={persons}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			addButtonText="Add Person"
			loading={loading}
			error={error}
			emptyMessage="No persons found"
			FormModal={PersonFormModal}
			ViewModal={PersonViewModal}
			endpoint="persons"
			nameKey="name"
			itemType="Person"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setPersons}
		/>
	);
};

export default PersonsPage;
