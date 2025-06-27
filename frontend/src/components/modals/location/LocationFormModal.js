import React, { useMemo } from "react";
import GenericModal from "../GenericModal";
import { getCountryCodeSync, getCountryNameSync } from "../../../utils/CountryUtils";
import { formFields, useCountries } from "../../rendering/FormRenders";

const LocationFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {
	// Use the countries hook for automatic loading
	const { countries, loading: loadingCountries } = useCountries();

	// Create fields with loaded countries
	const locationFields = useMemo(() => [
		formFields.postcode(),
		formFields.city(),
		formFields.country(countries, loadingCountries),
	], [countries, loadingCountries]);

	// Transform the initial data to work with react-select
	const transformInitialData = (data) => {
		if (!data.country || countries.length === 0) return data;

		// If the country is already a code, keep it
		if (countries.some((c) => c.value === data.country)) {
			return data;
		}

		// If the country is a name, convert to code
		const countryCode = getCountryCodeSync(data.country, countries);
		return {
			...data,
			country: countryCode,
		};
	};

	// Transform the form data before submission
	const transformFormData = (formData) => {
		if (!formData.country || countries.length === 0) return formData;

		// Convert country code back to name for API
		const countryName = getCountryNameSync(formData.country, countries);
		return {
			...formData,
			country: countryName,
		};
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

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			title="Location"
			fields={locationFields}
			endpoint="locations"
			onSuccess={onSuccess}
			initialData={transformInitialData(initialData)}
			isEdit={isEdit}
			validation={customValidation}
			transformFormData={transformFormData}
			size={size}
		/>
	);
};

export default LocationFormModal;