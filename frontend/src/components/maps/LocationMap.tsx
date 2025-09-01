import React, { useEffect, useState, useRef } from "react";
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
	locations: GeocodedLocation[];
}

const MapViewUpdater: React.FC<MapViewUpdaterProps> = ({ locations }) => {
	const map = useMap();

	useEffect(() => {
		if (locations.length === 0) {
			// If no locations, use default center
			map.setView([51.505, -0.09], 2);
		} else if (locations.length === 1) {
			// For single location, center on it
			const location = locations[0];
			// @ts-ignore
			map.setView([location.geocoded!.latitude, location.geocoded!.longitude], 10);
		} else {
			// For multiple locations, fit bounds to show all markers
			const bounds = L.latLngBounds(locations.map((loc) => [loc.geocoded!.latitude, loc.geocoded!.longitude]));
			map.fitBounds(bounds, { padding: [20, 20] });
		}
	}, [map, locations]);

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
	const mapRef = useRef<L.Map | null>(null);
	const containerRef = useRef<HTMLDivElement | null>(null);

	// Cleanup function to properly destroy the map
	useEffect(() => {
		return () => {
			// Cleanup when component unmounts
			if (mapRef.current) {
				try {
					mapRef.current.remove();
				} catch (error) {
					console.warn("Map cleanup error:", error);
				}
				mapRef.current = null;
			}
		};
	}, []);

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

	return (
		<div ref={containerRef} style={{ height }} className="border rounded overflow-hidden">
			<MapContainer style={{ height: "100%", width: "100%" }} className="leaflet-container">
				<MapViewUpdater locations={geocodedLocations} />
				<TileLayer
					attribution='&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
					url="https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png"
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
