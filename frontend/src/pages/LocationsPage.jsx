import React, { useEffect, useMemo } from "react";
import GenericTableWithModals, { useTableData } from "../components/tables/GenericTable";
import { LocationFormModal, LocationViewModal } from "../components/modals/LocationModal";
import LocationMap from "../components/maps/LocationMap";
import { columns } from "../components/rendering/view/TableColumnRenders";
import { useLoading } from "../contexts/LoadingContext";

const LocationsPage = () => {
	const { showLoading, hideLoading } = useLoading();
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
	} = useTableData("locations", [], {}, { key: "created_at", direction: "desc" });

	const tableColumns = [columns.name(), columns.city(), columns.postcode(), columns.country(), columns.createdAt()];

	useEffect(() => {
		if (loading) {
			showLoading("Loading Locations...");
		} else {
			hideLoading();
		}
		return () => {
			hideLoading();
		};
	}, [loading, showLoading, hideLoading]);

	return (
		<GenericTableWithModals
			title="Locations"
			data={allLocations}
			columns={tableColumns}
			sortConfig={sortConfig}
			onSort={setSortConfig}
			searchTerm={searchTerm}
			onSearchChange={setSearchTerm}
			loading={false}
			error={error}
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
			<div className="mt-4">
				<h5 className="mb-3">Location Map</h5>
				<LocationMap locations={allLocations} height="500px" />
			</div>
		</GenericTableWithModals>
	);
};

export default LocationsPage;
