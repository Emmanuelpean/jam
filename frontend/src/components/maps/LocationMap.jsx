import React, { useEffect, useState } from "react";
import { MapContainer, Marker, Popup, TileLayer, useMap } from "react-leaflet";
import { ProgressBar, Spinner } from "react-bootstrap";
import L from "leaflet";
import { geocodeLocationsBatch } from "../../services/GeoCoding";
import "leaflet/dist/leaflet.css";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: markerIcon2x,
    iconUrl: markerIcon,
    shadowUrl: markerShadow,
});

const MapViewUpdater = ({ locations }) => {
    const map = useMap();

    console.log("MapViewUpdater - locations:", locations);

    useEffect(() => {

        if (locations.length === 0) {
            // Default world view when no locationsW
            map.setView([20, 0], 2);
        } else if (locations.length === 1) {
            // Center on single location
            const location = locations[0];
            map.setView([location.geocoded.latitude, location.geocoded.longitude], 10);
        } else {
            // Fit bounds to show all markers
            const bounds = L.latLngBounds(
                locations.map((loc) => [loc.geocoded.latitude, loc.geocoded.longitude])
            );
            map.fitBounds(bounds, { padding: [20, 20] });
        }
    }, [map, JSON.stringify(
        locations.map((location) => ({
            id: location.id,
            city: location.modified_at,
        }))
    )]);

    return null;
};

const LocationMap = ({ locations = [], height = "400px" }) => {
    console.log("MapViewUpdater - locations:", locations);
    const [geocodedLocations, setGeocodedLocations] = useState([]);
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState({ current: 0, total: 0 });

    // Add logging to see what's changing
    const locationsKey = JSON.stringify(
        locations.map((location) => ({
            id: location.id,
            city: location.modified_at,
        }))
    );

    useEffect(() => {

        const geocodeLocations = async () => {
            if (locations.length === 0) {
                setGeocodedLocations([]);
                return;
            }

            setLoading(true);
            setProgress({ current: 0, total: locations.length });

            try {
                const results = await geocodeLocationsBatch(locations, (current, total) => {
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
    }, [locationsKey]);

    const formatLocationName = (location) => {
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
                                className="mb-2"
                            />
                            <small className="text-muted">
                                {progress.current} of {progress.total} locations processed
                            </small>
                        </>
                    ) : (
                        <p className="mb-2">Finding location on map...</p>
                    )}
                </div>
            </div>
        );
    }

    if (geocodedLocations.length === 0) {
        return (
            <div
                style={{ height }}
                className="d-flex flex-column justify-content-center align-items-center border rounded bg-light"
            >
                <div className="text-center p-4">
                    <div className="mb-3" style={{ fontSize: "2rem" }}>
                        🗺️
                    </div>
                    <h6 className="text-muted">No mappable locations found</h6>
                    <p className="text-muted mb-0 small">
                        {locations.length === 0
                            ? "Add some non-remote locations to see them on the map."
                            : "Could not find coordinates for any locations."}
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div>
            <div
                style={{
                    height,
                    borderRadius: "8px",
                    overflow: "hidden",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
                }}
            >
                <MapContainer
                    style={{ height: "100%", width: "100%" }}
                    scrollWheelZoom={true}
                >
                    <MapViewUpdater locations={geocodedLocations} />
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                    />

                    {geocodedLocations.map((location) => (
                        <Marker key={location.id} position={[location.geocoded.latitude, location.geocoded.longitude]}>
                            <Popup>
                                <div style={{ minWidth: "180px" }}>
                                    <h6 className="mb-2" style={{ color: "#2c3e50" }}>
                                        {formatLocationName(location)}
                                    </h6>
                                    {location.postcode && (
                                        <p className="mb-1">
                                            <strong>Postcode:</strong> {location.postcode}
                                        </p>
                                    )}
                                    <p className="mb-1">
                                        <strong>Coordinates:</strong>
                                        <br />
                                        <small className="text-muted">
                                            {location.geocoded.latitude.toFixed(4)},{" "}
                                            {location.geocoded.longitude.toFixed(4)}
                                        </small>
                                    </p>
                                </div>
                            </Popup>
                        </Marker>
                    ))}
                </MapContainer>
            </div>

            <div className="mt-2 d-flex justify-content-between align-items-center">
                <small className="text-muted">
                    📍 {geocodedLocations.length} of {locations.length} location
                    {locations.length !== 1 ? "s" : ""} shown
                </small>
            </div>
        </div>
    );
};

export default LocationMap;