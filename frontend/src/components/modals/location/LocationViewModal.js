import React from "react";
import GenericModal from "../GenericModal";
import LocationMap from "../../maps/LocationMap";
import { viewFields } from "../../rendering/ViewRenders";

const LocationViewModal = ({ show, onHide, location, onEdit, size }) => {
	if (!location) return null;

	let customContent;
	let fields = [];
	if (!location.remote) {
		fields = [viewFields.city(), viewFields.postcode(), viewFields.country()];
		customContent = (
			<>
				<div className="mb-4">
					<h6 className="mb-3">📍 Location on Map</h6>
					<LocationMap locations={[location]} height="300px" />
				</div>
			</>
		);
	} else {
		customContent = (
			<>
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
			</>
		);
	}

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="view"
			title="Location"
			data={location}
			viewFields={fields}
			onEdit={onEdit}
			size={size}
			customContent={customContent}
		/>
	);
};

export default LocationViewModal;
