import React, { JSX, useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { GeoLocationData } from "../../services/schemas/Base";
import { MAP_ATTRIBUTION, MAP_TILES } from "./tiles";
import "./LocationMap.scss";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
	iconRetinaUrl: markerIcon2x,
	iconUrl: markerIcon,
	shadowUrl: markerShadow,
});

export interface GeolocatedEntry {
	id: number;
	location?: string | null;
	attendance_type?: string | null;
	geolocation: GeoLocationData | null;
}

interface LocationMapProps {
	geolocatedEntry?: GeolocatedEntry[];
	height?: string;
	scrollWheelZoom?: boolean;
}

interface MapViewUpdaterProps {
	locations: GeolocatedEntry[];
}

type MappableLocation = GeolocatedEntry & { geolocation: GeoLocationData & { latitude: number; longitude: number } };

const isMappable = (location: GeolocatedEntry): location is MappableLocation =>
	location.geolocation != null && location.geolocation.latitude != null && location.geolocation.longitude != null;

const MapViewUpdater: React.FC<MapViewUpdaterProps> = ({ locations }: MapViewUpdaterProps) => {
	const map = useMap();

	useEffect((): (() => void) | void => {
		const updateView = (): void => {
			// Check if map container and pane are properly initialised
			if (!map || !map.getContainer() || !map.getPane("mapPane")) return;

			const geolocatedLocations: MappableLocation[] = locations.filter(isMappable);

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
						geolocatedLocations.map((loc) => [loc.geolocation.latitude, loc.geolocation.longitude])
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

const LocationMap: React.FC<LocationMapProps> = ({
	geolocatedEntry = [],
	height = "360px",
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

	const mappableLocations: MappableLocation[] = geolocatedEntry.filter(isMappable);
	const tileUrl: string = isDarkMode ? MAP_TILES.dark : MAP_TILES.light;

	if (mappableLocations.length === 0) {
		let icon = "bi-compass";
		let title = "No mappable locations found";
		let message = "Could not find coordinates for any of the provided locations.";

		if (geolocatedEntry.length === 1) {
			const [single] = geolocatedEntry;
			if (single!.geolocation === null) {
				icon = "bi-exclamation-triangle";
				title = "An error occurred when trying to locate this entry";
				message = "No geolocation data is available for this entry.";
			} else {
				icon = "bi-geo-alt";
				title = "This location could not be found";
				message = "The coordinates for this location could not be determined.";
			}
		}

		return (
			<div
				style={{ height }}
				className="d-flex flex-column justify-content-center align-items-center border rounded location-map-empty"
			>
				<div className="text-center p-4">
					<div className="mb-3" style={{ fontSize: "2rem" }}>
						<i className={icon}></i>
					</div>
					<h6 className="text-muted">{title}</h6>
					<p className="text-muted mb-0 small">{message}</p>
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
					borderRadius: "7px",
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
					<TileLayer attribution={MAP_ATTRIBUTION} url={tileUrl} />
					<MapViewUpdater locations={mappableLocations} />
					{mappableLocations.map(
						(location: MappableLocation): JSX.Element => (
							<Marker
								key={`${location.id}-${location.geolocation.latitude}-${location.geolocation.longitude}`}
								position={[location.geolocation.latitude, location.geolocation.longitude]}
							>
								<Popup>
									<div>
										<strong>{location.geolocation.query}</strong>
									</div>
								</Popup>
							</Marker>
						)
					)}
				</MapContainer>
			</div>
		</div>
	);
};

export default LocationMap;
