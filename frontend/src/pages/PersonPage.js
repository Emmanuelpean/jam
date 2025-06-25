import React from "react";
import GenericTableWithModals from "../components/tables/GenericTableWithModals";
import PersonFormModal from "../components/modals/person/PersonFormModal";
import PersonSwitchableModal from "../components/modals/person/PersonFormModal";
import { useTableData } from "../components/tables/Table";
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
			ViewModal={PersonSwitchableModal}
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