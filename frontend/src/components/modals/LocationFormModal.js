import React, { useEffect, useState } from "react";
import GenericModal from "../GenericModal";
import { fetchCountries, getCountryCodeSync, getCountryNameSync } from "../../utils/CountryUtils";

const LocationFormModal = ({ show, onHide, onSuccess, size, initialData = {}, isEdit = false }) => {
	const [countries, setCountries] = useState([]);
	const [loadingCountries, setLoadingCountries] = useState(false);

	// Load countries when component mounts
	useEffect(() => {
		const loadCountries = async () => {
			setLoadingCountries(true);
			try {
				const countriesList = await fetchCountries();
				setCountries(countriesList);
			} catch (error) {
				console.error("Failed to load countries:", error);
			} finally {
				setLoadingCountries(false);
			}
		};

		loadCountries();
	}, []);

	const formFields = [
		{
			name: "postcode",
			label: "Post Code",
			type: "text",
			required: false,
			placeholder: "Enter a post code",
		},
		{
			name: "city",
			label: "City",
			type: "text",
			required: false,
			placeholder: "Enter a city name",
		},
		{
			name: "country",
			label: "Country",
			type: "react-select",
			required: false,
			options: countries,
			placeholder: loadingCountries ? "Loading countries..." : "Search and select a country...",
			isSearchable: true,
			isClearable: true,
			isDisabled: loadingCountries,
		},
	];

	// Transform the initial data to work with react-select
	const transformInitialData = (data) => {
		if (!data.country || countries.length === 0) return data;

		// If country is already a code, keep it
		if (countries.some((c) => c.value === data.country)) {
			return data;
		}

		// If country is a name, convert to code
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
		const isRemote = formData.remote;

		const hasAnyValue = hasCity || hasPostcode || hasCountry || isRemote;

		if (!hasAnyValue) {
			errors.city =
				errors.country =
				errors.postcode =
				errors.remote =
					"Please fill in at least one field (city, postcode, country, or check remote)";
		}

		return errors;
	};

	return (
		<GenericModal
			show={show}
			onHide={onHide}
			title="Location"
			fields={formFields}
			endpoint="locations"
			onSuccess={onSuccess}
			initialData={transformInitialData(initialData)}
			isEdit={isEdit}
			customValidation={customValidation}
			transformFormData={transformFormData}
			size={size}
		/>
	);
};

export default LocationFormModal;
