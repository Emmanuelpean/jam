import React, { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import { ProgressBar, Spinner } from "react-bootstrap";
import L from "leaflet";
import { geocodeLocationsBatch } from "../../services/GeoCoding";
import "leaflet/dist/leaflet.css";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { LocationCreate } from "../../services/Schemas";

interface GeocodedLocation extends LocationCreate {
	geocoded: {
		latitude: number;
		longitude: number;
	} | null;
}

interface LocationMapProps {
	locations?: LocationCreate[];
	height?: string;
}

interface Progress {
	current: number;
	total: number;
}

// Component to handle map view updates
interface MapViewUpdaterProps {
	center: [number, number];
	zoom: number;
	locations: GeocodedLocation[];
}

const MapViewUpdater: React.FC<MapViewUpdaterProps> = ({ center, zoom, locations }) => {
	const map = useMap();

	useEffect(() => {
		if (locations.length === 0) {
			// If no locations, just set the center and zoom
			map.setView(center, zoom);
		} else if (locations.length === 1) {
			// For single location, center on it
			map.setView(center, zoom);
		} else {
			// For multiple locations, fit bounds to show all markers
			const bounds = L.latLngBounds(locations.map((loc) => [loc.geocoded!.latitude, loc.geocoded!.longitude]));
			map.fitBounds(bounds, { padding: [20, 20] });
		}
	}, [map, center, zoom, locations]);

	return null;
};

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
	iconRetinaUrl: markerIcon2x,
	iconUrl: markerIcon,
	shadowUrl: markerShadow,
});

const LocationMap: React.FC<LocationMapProps> = ({ locations = [], height = "400px" }) => {
	const [geocodedLocations, setGeocodedLocations] = useState<GeocodedLocation[]>([]);
	const [loading, setLoading] = useState<boolean>(false);
	const [progress, setProgress] = useState<Progress>({ current: 0, total: 0 });

	const defaultCenter: [number, number] = [51.505, -0.09]; // London
	const defaultZoom = 6;

	useEffect(() => {
		const geocodeLocations = async (): Promise<void> => {
			if (locations.length === 0) {
				setGeocodedLocations([]);
				return;
			}

			setLoading(true);
			setProgress({ current: 0, total: locations.length });

			try {
				const results = await geocodeLocationsBatch(locations as any, (current: number, total: number) => {
					setProgress({ current, total });
				});

				// Filter out locations that couldn't be geocoded
				const validLocations = results.filter((loc) => loc.geocoded !== null);
				setGeocodedLocations(validLocations);
			} catch (err) {
				console.error("Error geocoding locations:", err);
			} finally {
				setLoading(false);
			}
		};

		geocodeLocations().then(() => null);
	}, [
		// Create a more stable dependency by stringifying the relevant location data
		JSON.stringify(
			locations.map((loc) => ({
				id: loc.id,
				city: loc.city,
				postcode: loc.postcode,
				country: loc.country,
			})),
		),
	]);

	const getMapCenter = (): [number, number] => {
		if (geocodedLocations.length === 0) return defaultCenter;

		const avgLat =
			geocodedLocations.reduce((sum, loc) => sum + loc.geocoded!.latitude, 0) / geocodedLocations.length;
		const avgLng =
			geocodedLocations.reduce((sum, loc) => sum + loc.geocoded!.longitude, 0) / geocodedLocations.length;

		return [avgLat, avgLng];
	};

	const calculateOptimalZoom = (): number => {
		if (geocodedLocations.length === 0) return defaultZoom;
		if (geocodedLocations.length === 1) return 12; // Reasonable zoom for single location

		// Calculate bounds of all locations
		const latitudes = geocodedLocations.map((loc) => loc.geocoded!.latitude);
		const longitudes = geocodedLocations.map((loc) => loc.geocoded!.longitude);

		const minLat = Math.min(...latitudes);
		const maxLat = Math.max(...latitudes);
		const minLng = Math.min(...longitudes);
		const maxLng = Math.max(...longitudes);

		// Calculate the distance spans
		const latSpan = maxLat - minLat;
		const lngSpan = maxLng - minLng;
		const maxSpan = Math.max(latSpan, lngSpan);

		// Determine zoom level based on geographic span
		// These thresholds provide good balance between showing all locations and being readable
		if (maxSpan > 50) return 3; // Continental/multi-country view
		if (maxSpan > 20) return 4; // Large country view
		if (maxSpan > 10) return 5; // Country/large region view
		if (maxSpan > 5) return 6; // Regional view
		if (maxSpan > 2) return 7; // State/province view
		if (maxSpan > 1) return 8; // Large metropolitan area
		if (maxSpan > 0.5) return 9; // Metropolitan area
		if (maxSpan > 0.2) return 10; // City area
		if (maxSpan > 0.1) return 11; // District area
		return 12; // Local area
	};

	const formatLocationName = (location: GeocodedLocation): string => {
		const parts = [location.city, location.country].filter(Boolean);
		return parts.length > 0 ? parts.join(", ") : "Unknown Location";
	};

	if (loading) {
		return (
			<div
				style={{ height }}
				className="d-flex flex-column justify-content-center align-items-center border rounded bg-light"
			>
				<Spinner animation="border" className="mb-3" />
				<div className="text-center">
					{progress.total > 1 ? (
						<>
							<p className="mb-2">Finding locations on map...</p>
							<ProgressBar
								now={(progress.current / progress.total) * 100}
								style={{ width: "200px" }}
								label={`${progress.current}/${progress.total}`}
							/>
						</>
					) : (
						<p className="mb-0">Loading map...</p>
					)}
				</div>
			</div>
		);
	}

	const mapCenter = getMapCenter();
	const mapZoom = calculateOptimalZoom();

	return (
		<div style={{ height }} className="border rounded overflow-hidden">
			<MapContainer
				center={mapCenter}
				zoom={mapZoom}
				style={{ height: "100%", width: "100%" }}
				className="leaflet-container"
			>
				<MapViewUpdater center={mapCenter} zoom={mapZoom} locations={geocodedLocations} />
				<TileLayer
					attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
					url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
				/>
				{geocodedLocations.map((location) => (
					<Marker key={location.id} position={[location.geocoded!.latitude, location.geocoded!.longitude]}>
						<Popup>
							<div>
								<strong>{formatLocationName(location)}</strong>
								{location.city && <div>City: {location.city}</div>}
								{location.postcode && <div>Postcode: {location.postcode}</div>}
								{location.country && <div>Country: {location.country}</div>}
							</div>
						</Popup>
					</Marker>
				))}
			</MapContainer>
		</div>
	);
};

export default LocationMap;
