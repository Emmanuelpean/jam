import React, { useState } from "react";
import GenericTable, {
	createGenericDeleteHandler,
	createTableActions,
	displayNameFunctions,
} from "../components/tables/GenericTable";
import PersonFormModal from "../components/modals/PersonFormModal";
import PersonViewModal from "../components/modals/PersonViewModal";
import { useTableData } from "../components/tables/Table";
import { useAuth } from "../contexts/AuthContext";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/AlertModal";

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
		getItemDisplayName: displayNameFunctions.contact,
		itemType: "Person",
	});

	// Define table columns
	const columns = [
		{
			key: "name", // Changed from "full_name"
			label: "Name",
			sortable: true,
			searchable: true,
			type: "text",
			// Custom search function that searches both first_name and last_name
			searchFields: ["first_name", "last_name", "email"], // Add multiple fields to search
			render: (person) => (
				<div>
					<strong>{`${person.first_name} ${person.last_name}`}</strong>
					{person.email && (
						<div className="small text-muted">
							<i className="bi bi-envelope me-1"></i>
							{person.email}
						</div>
					)}
				</div>
			),
		},
		{
			key: "company_name",
			label: "Company",
			sortable: true,
			searchable: true,
			type: "text",
			searchFields: ["company.name"], // Search nested company name
			render: (person) => person.company?.name,
		},
		{
			key: "phone",
			label: "Phone",
			sortable: false,
			searchable: true,
			type: "text",
			render: (person) =>
				person.phone ? (
					<a href={`tel:${person.phone}`} className="text-decoration-none">
						<i className="bi bi-telephone me-1"></i>
						{person.phone}
					</a>
				) : null,
		},
		{
			key: "linkedin_url",
			label: "LinkedIn",
			sortable: false,
			searchable: true,
			type: "text",
			render: (person) =>
				person.linkedin_url ? (
					<a
						href={person.linkedin_url}
						target="_blank"
						rel="noopener noreferrer"
						className="text-decoration-none"
					>
						<i className="bi bi-linkedin me-1"></i>
						Profile <i className="bi bi-box-arrow-up-right ms-1"></i>
					</a>
				) : null,
		},
		{
			key: "created_at",
			label: "Date Added",
			type: "date",
			sortable: true,
			searchable: false, // Dates typically aren't searchable via text
			render: (person) => new Date(person.created_at).toLocaleDateString(),
		},
	];

	// Create standardized actions using the utility function
	const tableActions = createTableActions([
		{ type: "view", onClick: handleView, title: "View person details" },
		{ type: "edit", onClick: handleEdit, title: "Edit person" },
		{ type: "delete", onClick: handleDelete, title: "Delete person" },
	]);

	const handleAddSuccess = (newPerson) => {
		addItem(newPerson);
	};

	return (
		<div className="container">
			<h2 className="my-4">People</h2>

			<GenericTable
				data={people}
				columns={columns}
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
