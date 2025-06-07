import React from "react";
import GenericModal from "../GenericModal";
import LocationMap from "../maps/LocationMap";

const LocationViewModal = ({ show, onHide, location, onEdit, size }) => {
	// Define view fields for location
	const viewFields = [
		{
			name: "postcode",
			label: "Postcode",
			type: "text",
		},
		{
			name: "city",
			label: "City",
			type: "text",
		},
		{
			name: "country",
			label: "Country",
			type: "text",
		},
	];

	if (!location) return null;

	// Custom content for map or remote note
	const customContent = (
		<>
			{/* Location fields are handled by GenericModal */}
			{/* Map or Remote Info */}
			{!location.remote ? (
				<div className="mb-4">
					<h6 className="mb-3">📍 Location on Map</h6>
					<LocationMap locations={[location]} height="300px" />
				</div>
			) : (
				<div className="mb-4 p-3 bg-light rounded">
					<div className="text-center">
						<div className="mb-2" style={{ fontSize: "2rem" }}>
							🏠
						</div>
						<h6 className="text-muted">Remote Location</h6>
						<p className="text-muted mb-0 small">
							This location allows remote work and doesn't have a physical address.
						</p>
					</div>
				</div>
			)}
		</>
	);

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Location"
			data={location}
			viewFields={viewFields}
			onEdit={onEdit}
			showEditButton={true}
			showSystemFields={true}
			size={size}
			customContent={customContent}
		/>
	);
};

export default LocationViewModal;
