import React, { useState } from "react";
import GenericTable, { createGenericDeleteHandler, createTableActions } from "../components/tables/GenericTable";
import PersonFormModal from "../components/modals/PersonFormModal";
import PersonViewModal from "../components/modals/PersonViewModal";
import { useTableData } from "../components/tables/Table";
import { useAuth } from "../contexts/AuthContext";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/AlertModal";
import { columns } from "../components/rendering/ColumnRenders";

const PersonPage = () => {
	const { token } = useAuth();
	const {
		data: people,
		setData: setPeople,
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

	const [showModal, setShowModal] = useState(false);
	const [showViewModal, setShowViewModal] = useState(false);
	const [showEditModal, setShowEditModal] = useState(false);
	const [selectedPerson, setSelectedPerson] = useState(null);

	const { alertState, showConfirm, showError, hideAlert } = useGenericAlert();

	// Handle view person
	const handleView = (person) => {
		setSelectedPerson(person);
		setShowViewModal(true);
	};

	// Handle edit person
	const handleEdit = (person) => {
		setSelectedPerson(person);
		setShowEditModal(true);
	};

	// Handle edit success
	const handleEditSuccess = (updatedPerson) => {
		updateItem(updatedPerson);
		setShowEditModal(false);
		setSelectedPerson(null);
	};

	// Handle edit modal close
	const handleEditModalClose = () => {
		setShowEditModal(false);
		setSelectedPerson(null);
	};

	// Create reusable delete handler using the generic function
	const handleDelete = createGenericDeleteHandler({
		endpoint: "persons",
		token,
		showConfirm,
		showError,
		removeItem,
		setData: setPeople,
		nameKey: "name",
		itemType: "Person",
	});

	// Define table columns
	const tableColumns = [
		columns.personName,
		columns.email,
		columns.company,
		columns.phone,
		columns.linkedinUrl,
		columns.createdAt,
	];

	// Create standardized actions using the utility function
	const tableActions = createTableActions([
		{ type: "view", onClick: handleView },
		{ type: "edit", onClick: handleEdit },
		{ type: "delete", onClick: handleDelete },
	]);

	const handleAddSuccess = (newPerson) => {
		addItem(newPerson);
	};

	return (
		<div className="container">
			<h2 className="my-4">People</h2>

			<GenericTable
				data={people}
				columns={tableColumns}
				actions={tableActions}
				sortConfig={sortConfig}
				onSort={setSortConfig}
				searchTerm={searchTerm}
				onSearchChange={setSearchTerm}
				onAddClick={() => setShowModal(true)}
				addButtonText="Add Person"
				loading={loading}
				error={error}
				emptyMessage="No people found"
			/>

			{/* Modals */}
			<PersonFormModal show={showModal} onHide={() => setShowModal(false)} onSuccess={handleAddSuccess} />

			<PersonFormModal
				show={showEditModal}
				onHide={handleEditModalClose}
				onSuccess={handleEditSuccess}
				initialData={selectedPerson || {}}
				isEdit={true}
			/>

			<PersonViewModal
				show={showViewModal}
				onHide={() => setShowViewModal(false)}
				person={selectedPerson}
				onEdit={handleEdit}
			/>

			{/* Alert Modal using GenericModal - handles both alerts and confirmations */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default PersonPage;
