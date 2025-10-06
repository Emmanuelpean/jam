import React from "react";
import DataTable from "../components/tables/DataTable";
import { LocationModal } from "../components/modals/LocationModal";
import LocationMap from "../components/maps/LocationMap";
import { tableColumns } from "../components/rendering/view/TableColumns";
import { LocationData } from "../services/Schemas";

const LocationsPage = () => {
	const columns = [
		tableColumns.name(),
		tableColumns.city(),
		tableColumns.postcode(),
		tableColumns.country(),
		tableColumns.jobCountLocation(),
		tableColumns.interviewCountLocation(),
		tableColumns.createdAt(),
	];

	const locationMap = (locationData: LocationData[]) => {
		return (
			<div className="mt-4">
				<h5 className="mb-3">Location Map</h5>
				<LocationMap locations={locationData} height="500px" />
			</div>
		);
	};

	return (
		<DataTable
			entityType="locations"
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			title="Locations"
			columns={columns}
			Modal={LocationModal}
			nameKey="name"
			itemType="Location"
			children={locationMap}
		></DataTable>
	);
};

export default LocationsPage;
