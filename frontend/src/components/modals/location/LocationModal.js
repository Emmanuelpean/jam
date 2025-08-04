import React from "react";
import GenericModal from "../GenericModal";
import { formFields, useCountries } from "../../rendering/FormRenders";
import { viewFields } from "../../rendering/ViewRenders";
import { locationsApi } from "../../../services/api";
import { useAuth } from "../../../contexts/AuthContext";

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
	const { token } = useAuth();
	const { countries, loading: loadingCountries } = useCountries();

	// Form fields for editing - MUST be called before any conditional returns
	let formFieldsArray = [];
	if (!location?.remote) {
		formFieldsArray = [formFields.city(), formFields.postcode(), formFields.country(countries, loadingCountries)];
	}

	// View fields for display
	let viewFieldsArray;
	if (!location?.remote) {
		viewFieldsArray = [[viewFields.city(), viewFields.postcode(), viewFields.country()], viewFields.locationMap()];
	} else {
		viewFieldsArray = [viewFields.locationMap({ label: "" })];
	}

	const fields = {
		form: formFieldsArray,
		view: viewFieldsArray,
	};

	// Custom validation to ensure at least one field is filled
	const customValidation = async (formData) => {
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

		if (Object.keys(errors).length === 0) {

			// Build query parameters for exact match
			const queryParams = {};

			// Only add non-empty fields to the query
			queryParams.city = formData.city && formData.city.trim() || null;
			queryParams.postcode = formData.postcode && formData.postcode.trim() || null;
			queryParams.country = formData.country && formData.country.trim() || null;

			// Query for locations with these exact parameters
			const matchingLocations = await locationsApi.getAll(token, queryParams);

			// Filter out the current location if we're editing
			const duplicates = matchingLocations.filter((existingLocation) => {
				return location?.id !== existingLocation.id;
			});

			if (duplicates.length > 0) {
				const duplicateName = duplicates[0].name;
				errors.city =
					errors.postcode =
					errors.country =
						`A location with these details already exists: "${duplicateName}"`;
			}
		}
		return errors;
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
			data={location || {}}
			fields={fields}
			endpoint={endpoint}
			onSuccess={onSuccess}
			onDelete={onDelete}
			validation={customValidation}
			transformFormData={transformFormData}
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
