import React, { useMemo } from "react";
import GenericModal from "../GenericModal";
import { formFields, useCountries } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import LocationMap from "../../maps/LocationMap";

export const LocationModal = ({
	show,
	onHide,
	location,
	onSuccess,
	onDelete,
	endpoint = "locations",
	submode = "view",
	size = "lg",
}) => {
	// Use the countries hook for automatic loading - MUST be called before any conditional returns
	const { countries, loading: loadingCountries } = useCountries();

	// Form fields for editing - MUST be called before any conditional returns
	const formFieldsArray = useMemo(
		() => [formFields.city(), formFields.postcode(), formFields.country(countries, loadingCountries)],
		[countries, loadingCountries],
	);

	// Don't render if we're in view mode but have no location data
	if (submode === "view" && !location?.id) {
		return null;
	}

	// View fields for display
	let viewFieldsArray = [];
	let customContent;

	if (!location?.remote) {
		viewFieldsArray = [[viewFields.city(), viewFields.postcode(), viewFields.country()]];
		customContent = (
			<>
				<div className="mb-4">
					<h6 className="mb-3">📍 Location on Map</h6>
					<LocationMap locations={location ? [location] : []} height="300px" />
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

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	// Custom validation to ensure at least one field is filled
	const customValidation = (formData) => {
		const errors = {};

		const hasCity = formData.city && formData.city.trim();
		const hasPostcode = formData.postcode && formData.postcode.trim();
		const hasCountry = formData.country && formData.country.trim();

		const hasAnyValue = hasCity || hasPostcode || hasCountry;

		if (!hasAnyValue) {
			errors.city =
				errors.country =
				errors.postcode =
					"Please fill in at least one field (city, postcode, or country)";
		}

		return errors;
	};

	const transformInitialData = (data) => {
		return {
			...data,
		};
	};

	const transformFormData = (data) => {
		return {
			...data,
			city: data.city?.trim() || null,
			postcode: data.postcode?.trim() || null,
			country: data.country?.trim() || null,
		};
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			mode="formview"
			submode={submode}
			title="Location"
			size={size}
			data={transformInitialData(location || {})}
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
			customValidation={customValidation}
			transformFormData={transformFormData}
			customContent={customContent}
		/>
	);
};

export const LocationFormModal = (props) => {
	// Determine the submode based on whether we have location data with an ID
	const submode = props.isEdit || props.location?.id ? "edit" : "add";
	return <LocationModal {...props} submode={submode} />;
};

// Wrapper for view modal
export const LocationViewModal = (props) => <LocationModal {...props} submode="view" />;

// Add default export
export default LocationFormModal;
