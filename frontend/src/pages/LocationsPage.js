import React, { useMemo } from "react";
import GenericTableWithModals from "../components/tables/GenericTableWithModals";
import LocationFormModal from "../components/modals/location/LocationFormModal";
import LocationViewModal from "../components/modals/location/LocationViewModal";
import LocationMap from "../components/maps/LocationMap";
import { useTableData } from "../components/tables/Table";
import { columns } from "../components/rendering/ColumnRenders";

const LocationsPage = () => {
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

	const tableColumns = [
		columns.name,
		columns.city,
		columns.postcode,
		columns.country,
		columns.createdAt
	];

	return (
		<GenericTableWithModals
			title="Locations"
			data={locations}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			addButtonText="Add Location"
			loading={loading}
			error={error}
			emptyMessage="No locations found"
			FormModal={LocationFormModal}
			ViewModal={LocationViewModal}
			endpoint="locations"
			nameKey="name"
			itemType="Location"
			addItem={addItem}
			updateItem={updateItem}
			removeItem={removeItem}
			setData={setLocations}
		>
			{/* Map below table */}
			<div className="mt-4">
				<h5 className="mb-3">Location Map</h5>
				<LocationMap locations={locations} height="500px" />
			</div>
		</GenericTableWithModals>
	);
};

export default LocationsPage;