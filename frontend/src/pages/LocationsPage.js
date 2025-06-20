import React, { useMemo, useState } from "react";
import GenericTable, { createGenericDeleteHandler, createTableActions } from "../components/tables/GenericTable";
import LocationFormModal from "../components/modals/LocationFormModal";
import LocationViewModal from "../components/modals/LocationViewModal";
import LocationMap from "../components/maps/LocationMap";
import { useTableData } from "../components/tables/Table";
import { useAuth } from "../contexts/AuthContext";
import useGenericAlert from "../hooks/useGenericAlert";
import AlertModal from "../components/AlertModal";
import { columns } from "../components/rendering/ColumnRenders";

const LocationsPage = () => {
	const { token } = useAuth();
	const {
		data: allLocations,
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

	// Filter out remote locations
	const locations = useMemo(() => {
		return allLocations?.filter((location) => !location.remote) || [];
	}, [allLocations]);

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
		showConfirm,
		showError,
		removeItem,
		setData: setLocations,
		nameKey: "name",
		itemType: "Location",
	});

	// Define table columns (without actions)
	const tableColumns = [columns.name, columns.city, columns.postcode, columns.country, columns.createdAt];

	// Create standardised actions using the utility function
	const tableActions = createTableActions([
		{ type: "view", onClick: handleView },
		{ type: "edit", onClick: handleEdit },
		{ type: "delete", onClick: handleDelete },
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
				columns={tableColumns}
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
				<LocationMap locations={locations} height="500px" />
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
