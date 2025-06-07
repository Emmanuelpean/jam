import React, { useState } from "react";
import GenericTable, {
	createGenericDeleteHandler,
	createTableActions,
	displayNameFunctions,
} from "../components/tables/GenericTable";
import LocationFormModal from "../components/modals/LocationFormModal";
import LocationViewModal from "../components/modals/LocationViewModal";
import LocationMap from "../components/maps/LocationMap";
import { useTableData } from "../components/tables/Table";
import { useAuth } from "../contexts/AuthContext";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/AlertModal";

const LocationsPage = () => {
	const { token } = useAuth();
	const {
		data: locations,
		setData: setLocations,
		loading,
		error,
		sortConfig,
		setSortConfig,
		searchTerm,
		setSearchTerm,
		addItem,
		updateItem,
		removeItem,
	} = useTableData("locations");

	const [showModal, setShowModal] = useState(false);
	const [showViewModal, setShowViewModal] = useState(false);
	const [showEditModal, setShowEditModal] = useState(false);
	const [selectedLocation, setSelectedLocation] = useState(null);

	const { alertState, showConfirm, showError, hideAlert } = useGenericAlert();

	// Handle view location
	const handleView = (location) => {
		setSelectedLocation(location);
		setShowViewModal(true);
	};

	// Handle edit location
	const handleEdit = (location) => {
		setSelectedLocation(location);
		setShowEditModal(true);
	};

	// Handle edit success
	const handleEditSuccess = (updatedLocation) => {
		updateItem(updatedLocation);
		setShowEditModal(false);
		setSelectedLocation(null);
	};

	// Handle edit modal close
	const handleEditModalClose = () => {
		setShowEditModal(false);
		setSelectedLocation(null);
	};

	// Create reusable delete handler using the generic function
	const handleDelete = createGenericDeleteHandler({
		endpoint: "locations",
		token,
		showConfirm, // Pass showConfirm instead of showConfirmation
		showError,
		removeItem,
		setData: setLocations,
		getItemDisplayName: displayNameFunctions.location,
		itemType: "Location",
	});

	// Define table columns (without actions)
	const columns = [
		{
			key: "city",
			label: "City",
			sortable: true,
			searchable: true,
		},
		{
			key: "postcode",
			label: "Postcode",
			sortable: true,
			searchable: true,
		},
		{
			key: "country",
			label: "Country",
			type: "category",
			sortable: true,
			searchable: true,
		},
		{
			key: "remote",
			label: "Remote",
			sortable: true,
			render: (location) => (
				<span className={`badge ${location.remote ? "bg-success" : "bg-secondary"}`}>
					{location.remote ? "Yes" : "No"}
				</span>
			),
		},
		{
			key: "created_at",
			label: "Date Added",
			type: "date",
			sortable: true,
			render: (item) => new Date(item.created_at).toLocaleDateString(),
		},
	];

	// Create standardised actions using the utility function
	const tableActions = createTableActions([
		{ type: "view", onClick: handleView, title: "View location details" },
		{ type: "edit", onClick: handleEdit, title: "Edit location" },
		{ type: "delete", onClick: handleDelete, title: "Delete location" },
	]);

	const handleAddSuccess = (newLocation) => {
		addItem(newLocation);
	};

	return (
		<div className="container">
			<h2 className="my-4">Locations</h2>

			{/* Table first */}
			<GenericTable
				data={locations}
				columns={columns}
				actions={tableActions}
				sortConfig={sortConfig}
				onSort={setSortConfig}
				searchTerm={searchTerm}
				onSearchChange={setSearchTerm}
				onAddClick={() => setShowModal(true)}
				addButtonText="Add Location"
				loading={loading}
				error={error}
				emptyMessage="No locations found"
			/>

			{/* Map below table */}
			<div className="mt-4">
				<h5 className="mb-3">Location Map</h5>
				<LocationMap locations={locations || []} height="500px" />
			</div>

			{/* Modals */}
			<LocationFormModal show={showModal} onHide={() => setShowModal(false)} onSuccess={handleAddSuccess} />

			<LocationFormModal
				show={showEditModal}
				onHide={handleEditModalClose}
				onSuccess={handleEditSuccess}
				initialData={selectedLocation || {}}
				isEdit={true}
			/>

			<LocationViewModal
				show={showViewModal}
				onHide={() => setShowViewModal(false)}
				location={selectedLocation}
				onEdit={handleEdit}
			/>

			{/* Alert Modal using GenericModal - handles both alerts and confirmations */}
			<AlertModal alertState={alertState} hideAlert={hideAlert} />
		</div>
	);
};

export default LocationsPage;
