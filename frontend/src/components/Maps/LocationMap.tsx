import React, { JSX, useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { LocationData } from "../../services/schemas/DataTables";
import { ScrapedJobData } from "../../services/schemas/Services";
import { GeoLocation } from "../../services/schemas/Base";
import "./LocationMap.css";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
	iconRetinaUrl: markerIcon2x,
	iconUrl: markerIcon,
	shadowUrl: markerShadow,
});

type MapLocation = LocationData | ScrapedJobData;

interface LocationMapProps {
	locations?: MapLocation[];
	height?: string;
	scrollWheelZoom?: boolean;
}

interface MapViewUpdaterProps {
	locations: MapLocation[];
}

const isScrapedJobData = (location: MapLocation): location is ScrapedJobData => {
	return "location_city" in location;
};

const formatLocationName = (location: MapLocation): string => {
	if (isScrapedJobData(location)) {
		const parts = [location.location_postcode, location.location_city, location.location_country].filter(Boolean);
		return parts.join(", ") || "Unknown Location";
	}
	return location.name;
};

type GeolocatedMapLocation = MapLocation & { geolocation: GeoLocation };

const MapViewUpdater: React.FC<MapViewUpdaterProps> = ({ locations }: MapViewUpdaterProps) => {
	const map = useMap();

	useEffect((): (() => void) | void => {
		const updateView = (): void => {
			// Check if map container and pane are properly initialized
			if (!map || !map.getContainer() || !map.getPane("mapPane")) return;

			const geolocatedLocations: GeolocatedMapLocation[] = locations.filter(
				(location: MapLocation): location is GeolocatedMapLocation => location.geolocation !== null,
			);

			try {
				// Stop any ongoing animations first
				map.stop();

				if (geolocatedLocations.length === 0) {
					map.setView([20, 0], 2, { animate: false });
				} else if (geolocatedLocations.length === 1) {
					const location = geolocatedLocations[0]!;
					map.setView([location.geolocation.latitude, location.geolocation.longitude], 10, {
						animate: false,
					});
				} else {
					const bounds = L.latLngBounds(
						geolocatedLocations.map((loc) => [loc.geolocation.latitude, loc.geolocation.longitude]),
					);
					map.fitBounds(bounds, { padding: [20, 20], animate: false });
				}
			} catch (e) {
				console.warn("Map view update failed:", e);
			}
		};

		// Wait for next frame to ensure DOM is ready
		const frameId = requestAnimationFrame(() => {
			map.whenReady(updateView);
		});

		return () => cancelAnimationFrame(frameId);
	}, [locations, map]);

	return null;
};

const MAP_TILES = {
	light: { url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" },
	dark: { url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" },
};

const LocationMap: React.FC<LocationMapProps> = ({
	locations = [],
	height = "400px",
	scrollWheelZoom = true,
}: LocationMapProps): JSX.Element => {
	// Track dark mode state
	const [isDarkMode, setIsDarkMode] = useState<boolean>((): boolean => {
		return document.documentElement.getAttribute("data-mode") === "dark";
	});

	// Listen for dark mode changes
	useEffect(() => {
		const observer = new MutationObserver((mutations: MutationRecord[]) => {
			mutations.forEach((mutation: MutationRecord): void => {
				if (mutation.type === "attributes" && mutation.attributeName === "data-mode") {
					const newMode: boolean = document.documentElement.getAttribute("data-mode") === "dark";
					setIsDarkMode(newMode);
				}
			});
		});

		observer.observe(document.documentElement, {
			attributes: true,
			attributeFilter: ["data-mode"],
		});

		return () => observer.disconnect();
	}, []);

	const geolocatedLocations = locations.filter((location: MapLocation) => !!location.geolocation);
	const currentTileConfig = isDarkMode ? MAP_TILES.dark : MAP_TILES.light;

	if (geolocatedLocations.length === 0) {
		return (
			<div
				style={{ height }}
				className="d-flex flex-column justify-content-center align-items-center border rounded location-map-empty"
			>
				<div className="text-center p-4">
					<div className="mb-3" style={{ fontSize: "2rem" }}>
						<i className="bi-compass"></i>
					</div>
					<h6 className="text-muted">No mappable locations found</h6>
					<p className="text-muted mb-0 small">
						{locations.length === 0
							? "Add some locations to see them on the map."
							: "Could not find coordinates for any locations."}
					</p>
				</div>
			</div>
		);
	}

	return (
		<div>
			<div
				className="location-map-container"
				style={{
					height,
					borderRadius: "8px",
					overflow: "hidden",
					boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
				}}
			>
				<MapContainer
					center={[20, 0]}
					zoom={2}
					style={{ height: "100%", width: "100%" }}
					scrollWheelZoom={scrollWheelZoom}
				>
					<TileLayer
						attribution={
							'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
						}
						url={currentTileConfig.url}
					/>
					<MapViewUpdater locations={geolocatedLocations} />
					{geolocatedLocations.map(
						(location): JSX.Element => (
							<Marker
								key={`${location.id}-${location.geolocation!.latitude}-${location.geolocation!.longitude}`}
								position={[location.geolocation!.latitude, location.geolocation!.longitude]}
							>
								<Popup>
									<div>
										<strong>{formatLocationName(location)}</strong>
									</div>
								</Popup>
							</Marker>
						),
					)}
				</MapContainer>
			</div>
		</div>
	);
};

export default LocationMap;
