import React, { useState, useEffect } from "react";
import GenericTable from "../components/tables/GenericTable";
import { LocationModal } from "../components/modals/LocationModal";
import LocationMap from "../components/maps/LocationMap";
import { tableColumns } from "../components/rendering/view/TableColumns";
import { api } from "../services/Api";
import { useAuth } from "../contexts/AuthContext";

const LocationsPage = () => {
	const { token } = useAuth();
	const [locations, setLocations] = useState<any[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [error, setError] = useState<string | null>(null);

	const columns = [
		tableColumns.name(),
		tableColumns.city(),
		tableColumns.postcode(),
		tableColumns.country(),
		tableColumns.jobCount(),
		tableColumns.interviewCount(),
		tableColumns.createdAt(),
	];

	// Fetch locations data
	const fetchLocations = async () => {
		setLoading(true);
		setError(null);
		try {
			const result = await api.get("locations", token);
			setLocations(result || []);
		} catch (err) {
			console.error("Error fetching locations:", err);
			setError("Failed to load locations. Please try again later.");
			setLocations([]);
		} finally {
			setLoading(false);
		}
	};

	useEffect(() => {
		if (token) {
			fetchLocations();
		}
	}, [token]);

	return (
		<GenericTable
			mode="controlled"
			data={locations}
			onDataChange={setLocations}
			loading={loading}
			error={error}
			initialSortConfig={{ key: "created_at", direction: "desc" }}
			title="Locations"
			columns={columns}
			Modal={LocationModal}
			nameKey="name"
			itemType="Location"
		>
			<div className="mt-4">
				<h5 className="mb-3">Location Map</h5>
				<LocationMap locations={locations} height="500px" />
			</div>
		</GenericTable>
	);
};

export default LocationsPage;
