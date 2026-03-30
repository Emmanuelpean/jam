import React from "react";
import DataTable from "../../components/DataTable/DataTable";
import { LocationModal } from "../../components/DataModal/LocationModal";
import LocationMap from "../../components/Maps/LocationMap";
import { tableColumns } from "../../components/rendering/view/TableColumns";
import { LocationData } from "../../services/schemas/DataTables";

const LocationsPage = () => {
	const columns = [
		tableColumns.nameColumn(),
		tableColumns.cityColumn(),
		tableColumns.postcodeColumn(),
		tableColumns.countryColumn(),
		tableColumns.jobCountLocationColumn(),
		tableColumns.interviewCountLocationColumn(),
		tableColumns.createdAtColumn(),
	];

	const locationMap = (locationData: LocationData[]) => {
		return (
			<div className="mt-4">
				<h5 className="mb-3">Location Map</h5>
				<LocationMap locations={locationData} height="450px" />
			</div>
		);
	};

	return (
		<DataTable
			entityType="location"
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			title="Locations"
			columns={columns}
			modalSize={"sm"}
			Modal={LocationModal}
			enableColumnConfig={true}
			children={locationMap}
		></DataTable>
	);
};

export default LocationsPage;
