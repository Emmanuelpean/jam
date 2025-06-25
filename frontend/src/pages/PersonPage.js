import React from "react";
import GenericTableWithModals from "../components/tables/GenericTableWithModals";
import PersonSwitchableModal from "../components/modals/person/PersonFormModal";
import { useTableData } from "../components/tables/Table";
import { columns } from "../components/rendering/ColumnRenders";

// Wrapper for form modal (add/edit mode)
const PersonFormModal = (props) => (
	<PersonSwitchableModal
		{...props}
		submode={props.person ? "edit" : "add"}
	/>
);

// Wrapper for view modal
const PersonViewModal = (props) => (
	<PersonSwitchableModal
		{...props}
		submode="view"
	/>
);

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